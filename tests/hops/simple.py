import logging

from coherent_lasers.common.hops.main import HOPSDevice, HOPSException, get_hops_manager


logging.basicConfig(level=logging.DEBUG)


def get_head_id(device: HOPSDevice) -> str:
    return device.send_command("?HID")


try:
    # Get the DLL version
    manager = get_hops_manager()
    print(f"HOPS DLL Version: {manager.version}")

    serials = manager._handles.values()
    print(f"Discovered HOPS devices: {serials}")
    # SERIAL1 = "A700467EP203"
    # SERIAL2 = "J687424BP914"
    # SERIAL3 = "R708588EQ173"

    devices = [HOPSDevice(serial) for serial in serials]

    print(f"Active devices: {manager._active_serials}")

    for device in devices:
        device_id = get_head_id(device)
        print(f"Device ID: {device_id}")
        device.close()

    print("All devices closed.")
    print(f"Active devices: {manager._active_serials}")

except HOPSException as e:
    print(f"HOPS Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
