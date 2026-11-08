#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::sync::Mutex;
use tauri::State;

struct SidecarConfig {
    ipc_token: String,
    backend_url: String,
}

#[tauri::command]
fn get_sidecar_connection(state: State<Mutex<SidecarConfig>>) -> Result<(String, String), String> {
    let cfg = state.lock().map_err(|_| "Failed to lock sidecar state")?;
    Ok((cfg.backend_url.clone(), cfg.ipc_token.clone()))
}

fn main() {
    let config = SidecarConfig {
        ipc_token: "af-local-ipc-token-2026".to_string(),
        backend_url: "http://127.0.0.1:8765".to_string(),
    };

    tauri::Builder::default()
        .manage(Mutex::new(config))
        .invoke_handler(tauri::generate_handler![get_sidecar_connection])
        .run(tauri::generate_context!())
        .expect("error while running Animation Forge Tauri application");
}
