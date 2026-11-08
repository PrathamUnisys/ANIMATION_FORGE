import ctypes
import json
import os
from typing import Any, Dict, Optional


class HumanConfirmationDeclinedError(PermissionError):
    pass


class WindowsReviewerUnavailableError(RuntimeError):
    pass


def _get_windows_reviewer_name() -> str:
    if os.name != "nt":
        raise WindowsReviewerUnavailableError("Windows reviewer authentication is available only on Windows")

    secur32 = ctypes.WinDLL("secur32", use_last_error=True)
    get_user_name = secur32.GetUserNameExW
    get_user_name.argtypes = [
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_wchar),
        ctypes.POINTER(ctypes.c_ulong),
    ]
    get_user_name.restype = ctypes.c_int

    size = ctypes.c_ulong(256)
    name = ctypes.create_unicode_buffer(size.value)
    if not get_user_name(2, name, ctypes.byref(size)):
        if size.value <= len(name):
            raise ctypes.WinError(ctypes.get_last_error())
        name = ctypes.create_unicode_buffer(size.value)
        if not get_user_name(2, name, ctypes.byref(size)):
            raise ctypes.WinError(ctypes.get_last_error())

    reviewer_name = name.value.strip()
    if not reviewer_name:
        raise WindowsReviewerUnavailableError("Windows did not provide a reviewer identity")
    return reviewer_name


def _show_native_confirmation(message: str) -> bool:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    message_box = user32.MessageBoxW
    message_box.argtypes = [
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_uint,
    ]
    message_box.restype = ctypes.c_int
    result = message_box(None, message,     "Animation Forge - Human Review", 0x00000004 | 0x00000030 | 0x00040000 | 0x00010000)
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return result == 6


def _quoted(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=True)


def confirm_windows_human_action(action_summary: str) -> str:
    reviewer_name = _get_windows_reviewer_name()
    message = (
        "Confirm this action as the signed-in Windows reviewer?\n\n"
        f"Windows account: {_quoted(reviewer_name)}\n\n"
        f"{action_summary}\n\n"
        "Choose Yes to confirm."
    )
    if not _show_native_confirmation(message):
        raise HumanConfirmationDeclinedError("Windows reviewer declined the action")
    return f"HUMAN_WINDOWS_{reviewer_name}"


def confirm_windows_human_decision(
    gate: Dict[str, Any],
    decision: str,
    comments: str,
    rationale: Optional[str] = None,
) -> str:
    summary = "\n".join(
        (
            f"Project: {_quoted(gate['project_id'])}",
            f"Deliverable: {_quoted(gate['target_type'])} {_quoted(gate['target_id'])}",
            f"Revision: {_quoted(gate['revision'])}",
            f"Decision: {_quoted(decision)}",
            f"Review comments: {_quoted(comments[:4000])}",
            f"Rationale for project memory: {_quoted((rationale or '')[:4000])}",
        )
    )
    return confirm_windows_human_action(summary)
