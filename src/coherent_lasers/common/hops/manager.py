import ctypes as C
from dataclasses import dataclass
import logging
import os

from coherent_lasers.common.hops.device import HOPSDevice

from . import DLL_DIR

HOPS_DLL = os.path.join(DLL_DIR, "CohrHOPS.dll")

MAX_DEVICES = 20
MAX_STRLEN = 100

COHRHOPS_OK = 0

LPULPTR = C.POINTER(C.c_ulonglong)
COHRHOPS_HANDLE = C.c_ulonglong
LPDWORD = C.POINTER(C.c_ulong)
LPSTR = C.c_char_p
INT32 = C.c_int32


class HOPSException(Exception):
    ERROR_MESSAGES = {
        -3: "Invalid command",
        -100: "Secondary DLL not found",
    }

    def __init__(self, message: str, code: str | None = None) -> None:
        full_message = f"{message}: {self.ERROR_MESSAGES.get(code, f'Unknown error code: {code}')}"
        super().__init__(full_message)
        self.message = full_message
        self.code = code


class HOPSDevices:
    """Data structure to hold a list of HOPS devices matching the C type COHRHOPS_HANDLE"""

    def __init__(self):
        # noinspection PyCallingNonCallable,PyTypeChecker
        self.devices = (COHRHOPS_HANDLE * MAX_DEVICES)()

    def __getitem__(self, index):
        return self.devices[index]

    def pointer(self):
        return self.devices

@dataclass
class HOPSDeviceStatus:
    serial: str
    handle: COHRHOPS_HANDLE
    isActive: bool


class HOPSManager:
    def __init__(self, dll_path=HOPS_DLL):
        self.log = logging.getLogger(__name__)

        self._dll = C.CDLL(dll_path)
        self._wrap_functions()

        self.devices_connected = HOPSDevices()
        self.number_of_devices_connected = C.c_ulong()
        self.devices_added = HOPSDevices()
        self.number_of_devices_added = C.c_ulong()
        self.devices_removed = HOPSDevices()
        self.number_of_devices_removed = C.c_ulong()

        self.serials: dict[COHRHOPS_HANDLE, str] = {}

        self.devices: dict[COHRHOPS_HANDLE,  HOPSDevice] = {}

        self._initialize_devices()

    def __repr__(self):
        return f"HOPSDeviceManager with {len(self.devices)} devices: {self.serials}"

    @property
    def version(self) -> str:
        buffer = C.create_string_buffer(MAX_STRLEN)
        res = self._get_dll_version(buffer)
        if res == COHRHOPS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise Exception(f"Error getting DLL version: {res}")

    def get_device_serial(self, handle: COHRHOPS_HANDLE) -> str:
        response = C.create_string_buffer(MAX_STRLEN)
        res = self._send_command(handle, "?HID".encode("utf-8"), response)
        if res == COHRHOPS_OK:
            return response.value.decode("utf-8").strip()
        else:
            raise HOPSException(f"Error getting serial number for handle {handle}", res)

    def get_device_handle(self,*, serial: str) -> COHRHOPS_HANDLE:
        for handle, ser in self.serials.items():
            if serial == ser:
                return handle
        self._initialize_devices()
        handle = next(k for k,v in self.serials.items() if v == serial)
        if handle:
            return handle
        raise HOPSException(f"Device with serial no: {serial} could not be found")

    def close_device(self,*, handle: COHRHOPS_HANDLE) -> None:
        res = self._close(handle)
        if res == COHRHOPS_OK:
            if handle in self.serials:
                self.serials.pop(handle)
        else:
            raise HOPSException("Error closing handle", res)

    def send_device_command(self, command: str,*,handle: COHRHOPS_HANDLE) -> str:
        response = C.create_string_buffer(MAX_STRLEN)
        res = self._send_command(handle, command.encode(), response)
        if res == COHRHOPS_OK:
            return response.value.decode("utf-8")
        else:
            raise HOPSException("Error sending command", res)

    def close(self):
        self._refresh_device_info()
        for handle in self.devices_connected[: self.number_of_devices_connected.value]:
            self._close(handle)

    def __del__(self):
        self.close()

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

        self._get_dll_version = self._dll.CohrHOPS_GetDLLVersion
        self._get_dll_version.argtypes = [LPSTR]
        self._get_dll_version.restype = int

        self._check_for_devices = self._dll.CohrHOPS_CheckForDevices
        self._check_for_devices.argtypes = [LPULPTR, LPDWORD, LPULPTR, LPDWORD, LPULPTR, LPDWORD]
        self._check_for_devices.restype = int

    def _refresh_device_info(self) -> None:
        res = self._check_for_devices(
            self.devices_connected.pointer(),
            C.byref(self.number_of_devices_connected),
            self.devices_added.pointer(),
            C.byref(self.number_of_devices_added),
            self.devices_removed.pointer(),
            C.byref(self.number_of_devices_removed),
        )
        if res != COHRHOPS_OK:
            raise HOPSException(f"Error checking for devices", res)
        
        # if self.number_of_devices_connected.value > 0:
        #     for ser, device in self.devices.items():
        #         if device.handle not in 

    def _initialize_devices(self):
        self._refresh_device_info()

        if self.number_of_devices_connected.value > 0:
            self.serials.clear()
            for handle in self.devices_connected[: self.number_of_devices_connected.value]:
                self._initialize_device_by_handle(handle=handle)
        else:
            self.log.debug("No devices connected")

    def _initialize_device_by_handle(self, handle: COHRHOPS_HANDLE) -> None:
        headtype = C.create_string_buffer(MAX_STRLEN)
        res = self._initialize_handle(handle, headtype)
        # if res != COHRHOPS_OK:
        #     raise HOPSException("Error initializing device")
        serial = self.get_device_serial(handle=handle)


        self.serials[handle] = serial

    def initialize_device(self, serial: str):
        if serial not in self.devices:
            pass
        device = self.devices[serial]
        if device.handle in self.devices_connected.devices:
            if not device.isActive:
                headtype = C.create_string_buffer(MAX_STRLEN)
                res = self._initialize_handle(device.handle, headtype)
                if res != COHRHOPS_OK:
                    raise HOPSException(f"Error initializing device: {device}")
