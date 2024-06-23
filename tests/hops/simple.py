from coherent_lasers.common.hops.hops_device import HOPSManager

import os
import ctypes as C

HOPS_DLL = "C:\\Program Files (x86)\\Coherent\\HOPS\\CohrHOPS.dll"
os.add_dll_directory(os.getcwd())
dll = C.CDLL(HOPS_DLL)

LPSTRING = C.Array[C.c_char]
LPDWORD = C.POINTER(C.c_ulong)

get_dll_version = dll.CohrHOPS_GetDLLVersion
get_dll_version.argtypes = [LPSTRING]

buffer: LPSTRING = C.create_string_buffer(100)


def print_buffer():
    print(buffer.value.decode("utf-8"))


get_dll_version(buffer)
print_buffer()

devices_connected = LPDWORD()
number_of_devices_connected = LPDWORD()
devices_added = LPDWORD()
number_of_devices_added = LPDWORD()
devices_removed = LPDWORD()
number_of_devices_removed = LPDWORD()

devices_connected.contents = C.c_ulong(0)
number_of_devices_connected.contents = C.c_ulong(0)
devices_added.contents = C.c_ulong(0)
number_of_devices_added.contents = C.c_ulong(0)
devices_removed.contents = C.c_ulong(0)
number_of_devices_removed.contents = C.c_ulong(0)


def print_devices():
    if devices_connected and devices_connected.contents is not None:
        print("Devices connected: ", devices_connected.contents.value)
    if number_of_devices_connected and number_of_devices_connected.contents is not None:
        print("Number of devices connected: ", number_of_devices_connected.contents.value)
    if devices_added and devices_added.contents is not None:
        print("Devices added: ", devices_added.contents.value)
    if number_of_devices_added and number_of_devices_added.contents is not None:
        print("Number of devices added: ", number_of_devices_added.contents.value)
    if devices_removed and devices_removed.contents is not None:
        print("Devices removed: ", devices_removed.contents.value)
    if number_of_devices_removed and number_of_devices_removed.contents is not None:
        print("Number of devices removed: ", number_of_devices_removed.contents.value)


check_for_devices = dll.CohrHOPS_CheckForDevices
check_for_devices.argtypes = [LPDWORD, LPDWORD, LPDWORD, LPDWORD, LPDWORD, LPDWORD]

check_for_devices(
    devices_connected,
    number_of_devices_connected,
    devices_added,
    number_of_devices_added,
    devices_removed,
    number_of_devices_removed,
)
print_devices()


manager = HOPSManager()

print(manager.dll_version)
