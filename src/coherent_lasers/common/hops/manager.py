import ctypes as C
import logging
import os

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

    def __init__(self, message: str, code: str) -> None:
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


class HOPSManager:
    def __init__(self, dll_path=HOPS_DLL):
        self.log = logging.getLogger(__name__)

        self._dll = C.CDLL(dll_path)
        self._wrap_functions()

        self.devices: dict[str, COHRHOPS_HANDLE] = {}
        self._initialize_devices()

    def __repr__(self):
        return f"HOPSDeviceManager with {len(self.devices)} devices: {self.devices}"

    @property
    def version(self) -> str:
        buffer = C.create_string_buffer(MAX_STRLEN)
        res = self._get_dll_version(buffer)
        if res == COHRHOPS_OK:
            return buffer.value.decode("utf-8")
        else:
            raise Exception(f"Error getting DLL version: {res}")

    def get_device_handle(self, serial: str) -> COHRHOPS_HANDLE:
        handle = self.devices.get(serial)
        if handle is None:
            raise ValueError(f"Device with serial number {serial} not found")
        return handle

    def initialize_device(self, *, handle: COHRHOPS_HANDLE | None, serial: str | None = None) -> dict:
        handle = self._get_device_handle(serial) if handle is None else handle
        return self._initialize_device_by_handle(handle)

    def close_device(self, *, handle: COHRHOPS_HANDLE | None, serial: str | None = None) -> None:
        handle = self._get_device_handle(serial) if handle is None else handle
        res = self._close(handle)
        if res != COHRHOPS_OK:
            raise HOPSException("Error closing handle", res)

    def send_device_command(self, command: str, serial: str) -> str:
        handle = self._get_device_handle(serial)
        response = C.create_string_buffer(MAX_STRLEN)
        res = self._send_command(handle, command.encode(), response)
        if res == COHRHOPS_OK:
            return response.value.decode("utf-8")
        else:
            raise HOPSException("Error sending command", res)

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

    def _initialize_devices(self):
        devices_connected = HOPSDevices()
        number_of_devices_connected = C.c_ulong()
        devices_added = HOPSDevices()
        number_of_devices_added = C.c_ulong()
        devices_removed = HOPSDevices()
        number_of_devices_removed = C.c_ulong()

        res = self._check_for_devices(
            devices_connected.pointer(),
            C.byref(number_of_devices_connected),
            devices_added.pointer(),
            C.byref(number_of_devices_added),
            devices_removed.pointer(),
            C.byref(number_of_devices_removed),
        )

        if res != COHRHOPS_OK:
            raise HOPSException(f"Error checking for devices", res)

        if number_of_devices_connected.value > 0:
            for handle in devices_connected[: number_of_devices_connected.value]:
                self._initialize_device_by_handle(handle)
        else:
            self.log.debug("No devices connected")

    def _initialize_device_by_handle(self, handle: COHRHOPS_HANDLE) -> dict:
        headtype = C.create_string_buffer(MAX_STRLEN)
        res = self._initialize_handle(handle, headtype)
        if res == COHRHOPS_OK:
            serial = self._get_device_serial(handle)
            self.devices[serial] = handle
            self.log.debug(f"Device {serial} initialized with handle {handle}")
            return {"serial": serial, "handle": handle}
        else:
            raise HOPSException("Error initializing device", res)

    def _get_device_serial(self, handle: COHRHOPS_HANDLE) -> str:
        response = C.create_string_buffer(MAX_STRLEN)
        res = self._send_command(handle, "?HID".encode("utf-8"), response)
        if res == COHRHOPS_OK:
            return response.value.decode("utf-8").strip()
        else:
            raise Exception(f"Error sending command to handle {handle}: {res}")
