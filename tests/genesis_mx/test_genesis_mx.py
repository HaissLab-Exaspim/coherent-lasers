import time
import pytest
from coherent_lasers.common.hops.main import get_hops_manager
from coherent_lasers.genesis_mx.driver import GenesisMX


manager = get_hops_manager()
serials = list(manager._handles.values())
SERIAL1 = "A700467EP203"
SERIAL2 = "J687424BP914"
SERIAL3 = "R708588EQ173"
if not serials:
    raise RuntimeError("No HOPS devices found.")
print(f"Discovered HOPS devices: {serials}")

SERIAL_NO = SERIAL3


def wait_to_stabilize_power():
    time.sleep(1)  # Wait for power to stabilize


@pytest.fixture(scope="module")
def laser():
    laser = GenesisMX(SERIAL_NO)  # Use the first discovered device
    yield laser
    laser.disable()


def test_connection(laser):
    assert laser.hops is not None


def test_read_power(laser):
    power = laser.power_mw
    assert isinstance(power, float)
    assert power >= 0


def test_set_power(laser):
    # make sure the interlock is not active
    if not laser.is_interlocked:
        # assert laser.is_interlocked
        return
    original_power = laser.power_setpoint_mw
    test_power = min(original_power + 10, laser.ldd_current_limit)  # Ensure we don't exceed limits

    laser.power_setpoint_mw = test_power
    assert pytest.approx(laser.power_setpoint_mw, abs=1) == test_power  # Allow for small discrepancies
    wait_to_stabilize_power()
    assert pytest.approx(laser.power_mw, abs=1) == test_power

    laser.power_setpoint_mw = original_power
    assert pytest.approx(laser.power_setpoint_mw, abs=1) == original_power
    wait_to_stabilize_power()
    assert pytest.approx(laser.power_mw, abs=1) == original_power


# @pytest.mark.parametrize(
#     "temperature_attr", ["temperature_c", "shg_temperature_c", "brf_temperature_c", "etalon_temperature_c"]
# )
# def test_temperatures(laser, temperature_attr):
#     temperature = getattr(laser, temperature_attr)
#     assert isinstance(temperature, float)
#     assert 10 <= temperature <= 50  # Assuming normal operating temperatures


# def test_enable_disable(laser):
#     initial_state = laser.is_enabled

#     if not initial_state:
#         laser.enable()
#         assert laser.is_enabled

#     laser.disable()
#     assert not laser.is_enabled

#     # Return to initial state
#     if initial_state:
#         laser.enable()


# def test_alarms(laser):
#     alarms = laser.alarms
#     assert isinstance(alarms, list)
#     # Check if NO_FAULT is present or if there are specific alarms
#     assert any(alarm.name == "NO_FAULT" for alarm in alarms) or len(alarms) > 0


# @pytest.mark.slow
# def test_long_duration_stability(laser):
#     initial_power = laser.power_mw
#     for _ in range(60):  # Test for 1 minute
#         assert abs(laser.power_mw - initial_power) < 5  # Assuming stability within 5mW
#         pytest.sleep(1)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
