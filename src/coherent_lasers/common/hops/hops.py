import ctypes as C
import logging
import os
from typing import Dict

# Constants
DLL_DIR = os.path.dirname(os.path.abspath(__file__))
HOPS_DLL = os.path.join(DLL_DIR, "CohrHOPS.dll")
MAX_DEVICES = 20
MAX_STRLEN = 100
COHRHOPS_OK = 0

# C types
LPULPTR = C.POINTER(C.c_ulonglong)
COHRHOPS_HANDLE = C.c_ulonglong
LPDWORD = C.POINTER(C.c_ulong)
LPSTR = C.c_char_p

class HOPSException(Exception):
    pass

class HOPSDevices:
    def __init__(self):
        self.devices = (COHRHOPS_HANDLE * MAX_DEVICES)()

    def __getitem__(self, index):
        return self.devices[index]

    def pointer(self):
        return self.devices

class HOPSManager:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self._devices: Dict[str, 'HOPSDevice'] = {}
        self._handles: Dict[str, COHRHOPS_HANDLE] = {}
        self._dll = C.CDLL(HOPS_DLL)
        self._wrap_functions()
        
        self.devices_connected = HOPSDevices()
        self.number_of_devices_connected = C.c_ulong()
        self.devices_added = HOPSDevices()
        self.number_of_devices_added = C.c_ulong()
        self.devices_removed = HOPSDevices()
        self.number_of_devices_removed = C.c_ulong()

        self._refresh_devices()

    def _wrap_functions(self):
        self._initialize_handle = self._dll.CohrHOPS_InitializeHandle
        self._initialize_handle.argtypes = [COHRHOPS_HANDLE, LPSTR]
        self._initialize_handle.restype = int

        self._send_command = self._dll.CohrHOPS_SendCommand
        self._send_command.argtypes = [COHRHOPS_HANDLE, LPSTR, LPSTR]
        self._send_command.restype = int

        self._close = self._dll.CohrHOPS_Close
        self._close.argtypes = [COHRHOPS_HANDLE]
        self._close.restype = int

        self._check_for_devices = self._dll.CohrHOPS_CheckForDevices
        self._check_for_devices.argtypes = [LPULPTR, LPDWORD, LPULPTR, LPDWORD, LPULPTR, LPDWORD]
        self._check_for_devices.restype = int

    def _refresh_devices(self):
        self.log.debug("Starting device refresh")
        res = self._check_for_devices(
            self.devices_connected.pointer(),
            C.byref(self.number_of_devices_connected),
            self.devices_added.pointer(),
            C.byref(self.number_of_devices_added),
            self.devices_removed.pointer(),
            C.byref(self.number_of_devices_removed),
        )
        if res != COHRHOPS_OK:
            raise HOPSException(f"Error checking for devices: {res}")
        
        self.log.debug(f"Refresh complete. Connected: {self.number_of_devices_connected.value}")

        for i in range(self.number_of_devices_connected.value):
            handle = self.devices_connected[i]
            serial = self._get_device_serial(handle)
            self._handles[serial] = handle
            self.log.debug(f"Device connected: {serial}")

    def _get_device_serial(self, handle: COHRHOPS_HANDLE) -> str:
        response = C.create_string_buffer(MAX_STRLEN)
        res = self._send_command(handle, "?HID".encode("utf-8"), response)
        if res != COHRHOPS_OK:
            raise HOPSException(f"Error getting serial number for handle {handle}")
        return response.value.decode("utf-8").strip()

    def get_device_handle(self, serial: str) -> COHRHOPS_HANDLE:
        self._refresh_devices()
        if serial not in self._handles:
            raise HOPSException(f"Device with serial {serial} not found")
        return self._handles[serial]

    def send_command(self, serial: str, command: str) -> str:
        handle = self.get_device_handle(serial)
        response = C.create_string_buffer(MAX_STRLEN)
        res = self._send_command(handle, command.encode(), response)
        if res != COHRHOPS_OK:
            raise HOPSException(f"Error sending command to device {serial}")
        return response.value.decode("utf-8")

    def close_device(self, serial: str):
        if serial in self._handles:
            handle = self._handles[serial]
            res = self._close(handle)
            if res != COHRHOPS_OK:
                raise HOPSException(f"Error closing device {serial}")
            del self._handles[serial]
            if serial in self._devices:
                del self._devices[serial]

    def create_device(self, serial: str) -> 'HOPSDevice':
        if serial not in self._devices:
            self._devices[serial] = HOPSDevice(serial, self)
        return self._devices[serial]

    def close_all_devices(self):
        for serial in list(self._handles.keys()):
            self.close_device(serial)

    def __del__(self):
        self.close_all_devices()

class HOPSDevice:
    def __init__(self, serial: str, manager: HOPSManager):
        self.serial = serial
        self._manager = manager

    def send_command(self, command: str) -> str:
        return self._manager.send_command(self.serial, command)

    def close(self):
        self._manager.close_device(self.serial)

def get_hops_device(serial: str) -> HOPSDevice:
    manager = HOPSManager()
    return manager.create_device(serial)

