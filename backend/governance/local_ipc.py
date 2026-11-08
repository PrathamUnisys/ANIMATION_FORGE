import os
import secrets
from typing import Optional

from fastapi import Header, HTTPException, Request


TRUSTED_IPC_ORIGINS = {
    "http://127.0.0.1:1420",
    "http://tauri.localhost",
    "tauri://localhost",
}
IPC_TOKEN_ENVIRONMENT_VARIABLE = "ANIMATION_FORGE_IPC_TOKEN"
MINIMUM_IPC_TOKEN_LENGTH = 43


def verify_local_ipc_token(
    request: Request,
    x_forge_token: Optional[str] = Header(default=None),
) -> str:
    origin = request.headers.get("origin")
    if origin and origin not in TRUSTED_IPC_ORIGINS:
        raise HTTPException(status_code=403, detail="Untrusted local IPC origin")

    expected_token = os.environ.get(IPC_TOKEN_ENVIRONMENT_VARIABLE, "")
    if len(expected_token) < MINIMUM_IPC_TOKEN_LENGTH:
        raise HTTPException(status_code=503, detail="Local IPC authentication is not configured")
    if x_forge_token is None or not secrets.compare_digest(
        x_forge_token.encode("utf-8"),
        expected_token.encode("utf-8"),
    ):
        raise HTTPException(status_code=401, detail="Unauthorized local IPC token")
    return x_forge_token
