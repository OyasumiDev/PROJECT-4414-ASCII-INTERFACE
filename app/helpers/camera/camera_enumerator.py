"""
camera_enumerator.py
Detects available video capture devices with real device names.
"""
import sys
import subprocess
import cv2  # type: ignore  (opencv-python has no type stubs)
import time


def _windows_camera_names() -> list[str]:
    """
    Returns device friendly names from Windows PnP (no camera probing needed).
    Queries both 'Camera' class (modern UVC) and 'Image' class (older USB cameras
    like Logitech C920 which register as imaging devices).
    """
    try:
        result = subprocess.run(
            [
                "powershell", "-NoProfile", "-Command",
                "Get-PnpDevice "
                "| Where-Object { ($_.Class -eq 'Camera' -or $_.Class -eq 'Image') "
                "                  -and $_.Status -eq 'OK' } "
                "| Select-Object -ExpandProperty FriendlyName",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return [l.strip() for l in result.stdout.splitlines() if l.strip()]
    except Exception:
        return []


def list_cameras_fast() -> list[tuple[int, str]]:
    """
    Listado rápido al arrancar — usa solo PnP (sin abrir cámaras con cv2).
    Los índices son secuenciales 0, 1, 2… en el orden que Windows reporta.
    Returns list of (cv2_index, display_name).
    """
    if sys.platform == "win32":
        names = _windows_camera_names()
        if names:
            return [(i, name) for i, name in enumerate(names)]
    return [(0, "Cámara 0")]


def enumerate_cameras(max_index: int = 4) -> list[tuple[int, str]]:
    """
    Full scan — opens each cv2 index to confirm it works, pairs with device names.
    Slower; meant for the Refresh button.
    Returns list of (cv2_index, display_name).
    """
    names = _windows_camera_names() if sys.platform == "win32" else []
    available: list[tuple[int, str]] = []
    cam_count = 0
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            label = names[cam_count] if cam_count < len(names) else f"Cámara {i}"
            available.append((i, label))
            cam_count += 1
            cap.release()
            # Small delay to allow Windows to fully release the camera
            time.sleep(0.1)
    return available
