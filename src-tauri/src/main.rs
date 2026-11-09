#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::{Duration, Instant};
use tauri::{Manager, State};
use tauri_plugin_shell::{
    process::{CommandChild, CommandEvent},
    ShellExt,
};

struct SidecarConfig {
    ipc_token: String,
    backend_url: String,
    child: Mutex<Option<CommandChild>>,
    healthy: Arc<AtomicBool>,
}

#[tauri::command]
fn get_sidecar_connection(state: State<'_, SidecarConfig>) -> Result<(String, String), String> {
    if !state.healthy.load(Ordering::Acquire) {
        return Err("The local backend sidecar is not running".to_string());
    }
    Ok((state.backend_url.clone(), state.ipc_token.clone()))
}

fn generate_ipc_token() -> Result<String, String> {
    let mut random_bytes = [0_u8; 32];
    fill_random(&mut random_bytes)?;
    Ok(random_bytes
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect())
}

#[cfg(windows)]
fn fill_random(bytes: &mut [u8]) -> Result<(), String> {
    use std::ffi::c_void;

    #[link(name = "bcrypt")]
    extern "system" {
        fn BCryptGenRandom(
            algorithm: *mut c_void,
            buffer: *mut u8,
            buffer_len: u32,
            flags: u32,
        ) -> i32;
    }

    let status = unsafe {
        BCryptGenRandom(
            std::ptr::null_mut(),
            bytes.as_mut_ptr(),
            bytes.len() as u32,
            0x0000_0002,
        )
    };
    if status != 0 {
        return Err(format!("Windows cryptographic RNG failed with status {status:#x}"));
    }
    Ok(())
}

#[cfg(unix)]
fn fill_random(bytes: &mut [u8]) -> Result<(), String> {
    std::fs::File::open("/dev/urandom")
        .and_then(|mut source| source.read_exact(bytes))
        .map_err(|error| format!("Could not read operating-system randomness: {error}"))
}

#[cfg(not(any(windows, unix)))]
fn fill_random(_bytes: &mut [u8]) -> Result<(), String> {
    Err("Secure IPC tokens are unsupported on this operating system".to_string())
}

fn select_backend_port() -> Result<u16, String> {
    let listener = TcpListener::bind(("127.0.0.1", 0))
        .map_err(|error| format!("Could not select a local backend port: {error}"))?;
    let port = listener
        .local_addr()
        .map_err(|error| format!("Could not read the selected backend port: {error}"))?
        .port();
    drop(listener);
    Ok(port)
}

fn wait_for_backend(token: &str, port: u16) -> Result<(), String> {
    let address = SocketAddr::from(([127, 0, 0, 1], port));
    let deadline = Instant::now() + Duration::from_secs(20);
    while Instant::now() < deadline {
        if let Ok(mut stream) = TcpStream::connect_timeout(&address, Duration::from_millis(250)) {
            stream
                .set_read_timeout(Some(Duration::from_secs(1)))
                .map_err(|error| format!("Could not configure backend readiness check: {error}"))?;
            let request = format!(
                "GET /api/health HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nX-Forge-Token: {token}\r\nConnection: close\r\n\r\n"
            );
            if stream.write_all(request.as_bytes()).is_ok() {
                let mut status = [0_u8; 64];
                if let Ok(bytes_read) = stream.read(&mut status) {
                    if status[..bytes_read].starts_with(b"HTTP/1.1 200")
                        || status[..bytes_read].starts_with(b"HTTP/1.0 200")
                    {
                        return Ok(());
                    }
                }
            }
        }
        thread::sleep(Duration::from_millis(200));
    }
    Err("The local backend did not become ready with its generated IPC token".to_string())
}

fn main() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let ipc_token = generate_ipc_token().map_err(std::io::Error::other)?;
            let backend_port = select_backend_port().map_err(std::io::Error::other)?;
            let command = app
                .shell()
                .sidecar("animation-forge-backend")
                .map_err(|error| std::io::Error::other(error.to_string()))?
                .env("ANIMATION_FORGE_IPC_TOKEN", &ipc_token)
                .env("ANIMATION_FORGE_PORT", backend_port.to_string())
                .set_process_group(true);
            let (mut events, child) = command
                .spawn()
                .map_err(|error| std::io::Error::other(error.to_string()))?;

            let healthy = Arc::new(AtomicBool::new(true));
            let monitor_health = Arc::clone(&healthy);
            tauri::async_runtime::spawn(async move {
                while let Some(event) = events.recv().await {
                    match event {
                        CommandEvent::Terminated(payload) => {
                            monitor_health.store(false, Ordering::Release);
                            eprintln!("Animation Forge backend exited: {:?}", payload);
                            break;
                        }
                        CommandEvent::Error(error) => {
                            eprintln!("Animation Forge backend error: {error}");
                        }
                        CommandEvent::Stdout(_) | CommandEvent::Stderr(_) => {}
                        _ => {}
                    }
                }
            });

            if let Err(startup_error) = wait_for_backend(&ipc_token, backend_port) {
                return match child.kill() {
                    Ok(()) => Err(std::io::Error::other(startup_error).into()),
                    Err(kill_error) => Err(std::io::Error::other(format!(
                        "{startup_error}; failed to stop the backend: {kill_error}"
                    ))
                    .into()),
                };
            }

            app.manage(SidecarConfig {
                ipc_token,
                backend_url: format!("http://127.0.0.1:{backend_port}"),
                child: Mutex::new(Some(child)),
                healthy,
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_sidecar_connection])
        .build(tauri::generate_context!())
        .expect("error while building Animation Forge Tauri application");

    app.run(|app_handle, event| {
        if let tauri::RunEvent::Exit = event {
            if let Some(state) = app_handle.try_state::<SidecarConfig>() {
                match state.child.lock() {
                    Ok(mut child) => {
                        if let Some(child) = child.take() {
                            if let Err(error) = child.kill() {
                                eprintln!("Could not stop Animation Forge backend: {error}");
                            }
                        }
                    }
                    Err(error) => eprintln!("Could not access backend process handle: {error}"),
                }
            }
        }
    });
}
