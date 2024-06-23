from threading import Lock
from typing import Any

from .manager import HOPSManager


def _get_threadsafe_manager() -> HOPSManager:
    if not hasattr(_get_threadsafe_manager, "instance"):
        with _get_threadsafe_manager._lock:
            if not hasattr(_get_threadsafe_manager, "instance"):
                _get_threadsafe_manager.instance = HOPSManager()
    return _get_threadsafe_manager.instance


_get_threadsafe_manager._lock = Lock()

hops_manager = _get_threadsafe_manager()


class HOPSDevice:

    def __init__(self, serial: str):
        self.serial = serial
        self._manager = hops_manager

    def send_command(self, command: str) -> None:
        self._manager.send_device_command(self.serial, command)

    def close(self):
        self._manager.close_device(self.serial)

    def __enter__(self) -> "HOPSDevice":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass  # Ignore errors during garbage collection
