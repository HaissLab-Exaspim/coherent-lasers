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
    _manager = hops_manager
    def __init__(self, serial: str):
        self.serial = serial
        self.handle = self._manager.get_device_handle(serial=self.serial)

    def send_command(self, command: str) -> None:
        self._manager.send_device_command(command, handle=self.handle)

    def close(self):
        self._manager.close_device(handle=self.handle)
