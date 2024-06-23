import logging
from coherent_lasers.common.hops.manager import HOPSManager, HOPSException
from coherent_lasers.common.hops.device import HOPSDevice

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def run_integration_tests():
    try:
        # Initialize the HOPSManager
        manager = HOPSManager()
        logger.info(f"HOPSManager initialized. Version: {manager.version}")

        # Check for connected devices
        logger.info(f"Connected devices: {manager.devices}")

        if not manager.devices:
            logger.warning("No devices found. Please connect a device and run the test again.")
            return

        # Test with the first connected device
        serial = list(manager.devices.keys())[0]
        device = HOPSDevice(serial)

        # Test sending commands
        test_commands = [
            "?HID",  # Get Head ID
            "?HTYPE",  # Get Head Type
            "?HH",  # Get Head Hours
            # Add more commands here based on your device's capabilities
        ]

        for cmd in test_commands:
            try:
                response = device.send_command(cmd)
                logger.info(f"Command '{cmd}' response: {response}")
            except HOPSException as e:
                logger.error(f"Error sending command '{cmd}': {e}")

        # Test closing the device
        device.close()
        logger.info("Device closed successfully")

        # Test re-opening the device
        device = HOPSDevice(serial)
        logger.info("Device re-opened successfully")

    except HOPSException as e:
        logger.error(f"HOPS Exception occurred: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
    finally:
        # Ensure all devices are closed
        if "manager" in locals():
            for serial in manager.devices:
                try:
                    manager.close_device(serial=serial)
                except Exception as e:
                    logger.error(f"Error closing device {serial}: {e}")


if __name__ == "__main__":
    run_integration_tests()
