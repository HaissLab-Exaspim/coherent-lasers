import logging

from coherent_lasers.common.hops.hops import HOPSException, HOPSManager, get_hops_device


logging.basicConfig(level=logging.DEBUG)

SERIAL1 = "A700467EP203"
SERIAL2 = "J687424BP914"

try:
    # Get the DLL version
    manager = HOPSManager()
    print(f"HOPS DLL Version: {manager.version}")

    # Create two devices
    device1 = get_hops_device(SERIAL1)
    device2 = get_hops_device(SERIAL2)

    # Send commands to the devices
    response1 = device1.send_command("?HID")
    print(f"Device 1 ({SERIAL1}) response: {response1}")

    response2 = device2.send_command("?HID")
    print(f"Device 2 ({SERIAL2}) response: {response2}")

    # Close the devices
    device1.close()
    device2.close()

except HOPSException as e:
    print(f"HOPS Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Ensure all devices are closed and resources are released
    if 'manager' in locals():
        manager.close_all_devices()
    print("All devices closed. Exiting.")