from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any


class ComfyUIError(RuntimeError):
    """Raised when ComfyUI cannot be reached or rejects a request."""


def _multipart(fields: dict[str, str], file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    buffer = bytearray()
    for name, value in fields.items():
        buffer += f"--{boundary}\r\n".encode()
        buffer += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        buffer += f"{value}\r\n".encode()
    buffer += f"--{boundary}\r\n".encode()
    buffer += (
        f'Content-Disposition: form-data; name="{file_field}"; filename="{file_path.name}"\r\n'
    ).encode()
    buffer += b"Content-Type: application/octet-stream\r\n\r\n"
    buffer += file_path.read_bytes()
    buffer += f"\r\n--{boundary}--\r\n".encode()
    return bytes(buffer), f"multipart/form-data; boundary={boundary}"


class ComfyUIClient:
    """Minimal, dependency-free HTTP client for a local ComfyUI server.

    Uses the documented built-in routes: /system_stats, /object_info, /models,
    /upload/image, /prompt, /queue, /history and /view.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:8188", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client_id = uuid.uuid4().hex

    # ---------------------------------------------------------------- helpers

    def _url(self, path: str, params: dict[str, str] | None = None) -> str:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        return url

    def _request(
        self,
        path: str,
        params: dict[str, str] | None = None,
        payload: Any = None,
        raw: bytes | None = None,
        content_type: str | None = None,
        expect_json: bool = True,
    ) -> Any:
        url = self._url(path, params)
        data = raw
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif content_type:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ComfyUIError(f"{path} returned HTTP {exc.code}: {detail[:800]}") from exc
        except urllib.error.URLError as exc:
            raise ComfyUIError(f"ComfyUI unreachable at {self.base_url}: {exc.reason}") from exc
        if not expect_json:
            return body
        try:
            return json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ComfyUIError(f"{path} returned a non-JSON response.") from exc

    # ------------------------------------------------------------------ reads

    def system_stats(self) -> dict[str, Any]:
        return self._request("/system_stats")

    def object_info(self, node_class: str | None = None) -> dict[str, Any]:
        path = f"/object_info/{node_class}" if node_class else "/object_info"
        return self._request(path)

    def list_models(self, folder: str) -> list[str]:
        return self._request(f"/models/{folder}")

    def queue_status(self) -> dict[str, Any]:
        return self._request("/queue")

    def history(self, prompt_id: str) -> dict[str, Any]:
        return self._request(f"/history/{prompt_id}")

    # ----------------------------------------------------------------- writes

    def upload_image(self, image_path: str | Path, subfolder: str = "", overwrite: bool = True) -> dict[str, Any]:
        path = Path(image_path)
        if not path.is_file():
            raise ComfyUIError(f"Cannot upload missing file: {path}")
        body, content_type = _multipart(
            {"type": "input", "overwrite": str(overwrite).lower(), "subfolder": subfolder},
            "image",
            path,
        )
        return self._request("/upload/image", raw=body, content_type=content_type)

    def queue_prompt(self, api_workflow: dict[str, Any]) -> dict[str, Any]:
        result = self._request(
            "/prompt", payload={"prompt": api_workflow, "client_id": self.client_id}
        )
        if not result.get("prompt_id"):
            raise ComfyUIError(f"ComfyUI rejected the workflow: {json.dumps(result)[:800]}")
        return result

    def view(self, filename: str, subfolder: str = "", file_type: str = "output") -> bytes:
        return self._request(
            "/view",
            params={"filename": filename, "subfolder": subfolder, "type": file_type},
            expect_json=False,
        )

    # ------------------------------------------------------------- generation

    def generate(
        self,
        api_workflow: dict[str, Any],
        poll_interval: float = 2.0,
        timeout: int = 900,
    ) -> dict[str, Any]:
        """Queue a workflow, wait for completion and return the output entries."""
        queued = self.queue_prompt(api_workflow)
        prompt_id = queued["prompt_id"]
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            history = self.history(prompt_id)
            record = history.get(prompt_id)
            if record:
                status = record.get("status", {})
                if status.get("status_str") == "error" or status.get("completed") is False:
                    raise ComfyUIError(
                        f"ComfyUI execution failed for {prompt_id}: "
                        f"{json.dumps(status.get('messages', status))[:800]}"
                    )
                if record.get("outputs"):
                    images = []
                    for node_output in record["outputs"].values():
                        for image in node_output.get("images", []):
                            images.append(
                                {
                                    "filename": image["filename"],
                                    "subfolder": image.get("subfolder", ""),
                                    "type": image.get("type", "output"),
                                }
                            )
                    return {"prompt_id": prompt_id, "outputs": images, "history": record}
            time.sleep(poll_interval)
        raise ComfyUIError(f"Timed out after {timeout}s waiting for ComfyUI prompt {prompt_id}")

    def fetch_image(self, image_entry: dict[str, Any]) -> bytes:
        return self.view(
            image_entry["filename"],
            image_entry.get("subfolder", ""),
            image_entry.get("type", "output"),
        )
