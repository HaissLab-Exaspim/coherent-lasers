from dataclasses import dataclass
from coherent_lasers.genesis_mx.commands import ReadCmds, WriteCmds, OperationModes, Alarms
from coherent_lasers.common.hops import HOPSDevice


@dataclass(frozen=True)
class GenesisMXTempMetric:
    temp: float
    voltage: float


@dataclass
class GenesisMXTempMetrics:
    main: GenesisMXTempMetric
    etalon: GenesisMXTempMetric
    brf: GenesisMXTempMetric
    shg: GenesisMXTempMetric

@dataclass(frozen=True)
class GenesisMXHeadInfo:
    serial: str
    type: str
    hours: str
    board_revision: str
    dio_status: str

@dataclass(frozen=True)
class GenesisMXEnableLoop:
    software: bool
    interlock: bool
    key: bool

    @property
    def enabled(self) -> bool:
        return self.software and self.interlock and self.key

    @property
    def ready(self) -> bool:
        return self.interlock and self.key and not self.software


class GenesisMX:
    def __init__(self, serial: str):
        self.serial = serial
        self.hops = HOPSDevice(self.serial)
        if not self.hops:
            raise ValueError(f"Failed to initialize laser with serial number {self.serial}")

    @property
    def mode(self) -> OperationModes:
        """Get the current mode of the laser: current mode or photomode."""
        mode_value = self.send_read_command(ReadCmds.CURRENT_MODE)
        return OperationModes(int(mode_value))

    @mode.setter
    def mode(self, value: OperationModes) -> None:
        """Set the mode of the laser."""
        self.send_write_command(WriteCmds.SET_MODE, value.value)

    @property
    def power_mw(self) -> float:
        """Get the current power of the laser."""
        return float(self.send_read_command(ReadCmds.POWER))

    @power_mw.setter
    def power_mw(self, value: float):
        """Set the power of the laser."""
        self.send_write_command(WriteCmds.SET_POWER, value)

    @property
    def power_setpoint_mw(self):
        """Get the current power setpoint of the laser."""
        return float(self.send_read_command(ReadCmds.POWER_SETPOINT))

    @property
    def ldd_current(self):
        """
        Get the LDD current of the laser.

        Measures the current supplied to the Laser Diode Driver (LDD).
        """
        return float(self.send_read_command(ReadCmds.LDD_CURRENT))

    @property
    def ldd_current_limit(self):
        """
        Get the LDD current limit of the laser.

        Measures the maximum current limit set for the Laser Diode Driver (LDD).
        """
        return float(self.send_read_command(ReadCmds.LDD_CURRENT_LIMIT))

    @property
    def enable_loop(self) -> GenesisMXEnableLoop:
        return GenesisMXEnableLoop(
            software=self.send_read_command(ReadCmds.SOFTWARE_SWITCH_STATE) == 1,
            interlock=self.send_read_command(ReadCmds.INTERLOCK_STATUS) == 1,
            key=self.send_read_command(ReadCmds.KEY_SWITCH_STATE) == 1,
        )

    def enable(self) -> GenesisMXEnableLoop:
        """Enable the laser."""
        if self.enable_loop.ready:
            self.send_write_command(WriteCmds.SET_SOFTWARE_SWITCH, 1)
            return self.enable_loop
        else:
            raise ValueError(f"Cannot enable laser {self.serial}. Check interlock and key switch: {self.enable_loop}")

    def disable(self) -> GenesisMXEnableLoop:
        """Disable the laser."""
        self.send_write_command(WriteCmds.SET_SOFTWARE_SWITCH, 0)
        return self.enable_loop

    @property
    def is_ldd_enabled(self) -> bool:
        """
        Get the LDD enable state of the laser.

        Reads whether the Laser Diode Driver (LDD) is enabled or disabled.
        """
        return self.send_read_command(ReadCmds.LDD_ENABLE_STATE) == 1

    # Flags

    @property
    def analog_input_enable(self) -> bool:
        """
        Get the analog input status of the laser.

        Reads the status of the analog input (enabled or disabled).
        """
        state = self.send_read_command(ReadCmds.ANALOG_INPUT_STATUS)
        return state == 1

    @analog_input_enable.setter
    def analog_input_enable(self, value: bool):
        """Set the analog input status of the laser."""
        self.send_write_command(WriteCmds.SET_ANALOG_INPUT, 1 if value else 0)

    @property
    def remote_control_enable(self) -> bool:
        """
        Get the remote control status of the laser.

        Reads whether remote control is enabled or disabled.
        """
        return self.send_read_command(ReadCmds.REMOTE_CONTROL_STATUS) == 1

    @remote_control_enable.setter
    def remote_control_enable(self, value: bool):
        """Set the remote control status of the laser."""
        self.send_write_command(WriteCmds.SET_REMOTE_CONTROL, 1 if value else 0)

    # Information

    @property
    def head(self) -> GenesisMXHeadInfo:
        """Get the laser head information."""
        return GenesisMXHeadInfo(
            serial=self.send_read_command(ReadCmds.HEAD_SERIAL),
            type=self.send_read_command(ReadCmds.HEAD_TYPE),
            hours=self.send_read_command(ReadCmds.HEAD_HOURS),
            board_revision=self.send_read_command(ReadCmds.HEAD_BOARD_REVISION),
            dio_status=self.send_read_command(ReadCmds.HEAD_DIO_STATUS),
        )

    @property
    def alarms(self) -> list[Alarms]:
        """Get the list of active alarms based on the fault code."""
        fault_code_value = int(self.send_read_command(ReadCmds.FAULT_CODE), 16)
        faults = Alarms.from_code(fault_code_value)
        return faults

    @property
    def tempurature_metrics(self) -> GenesisMXTempMetrics:
        return GenesisMXTempMetrics(
            main = GenesisMXTempMetric(
                temp=self.temperature_c
                voltage=self.main_tec_drive_v
            ),
            etalon=GenesisMXTempMetric(
                temp=self.send_read_command(ReadCmds.ETALON_TEMPERATURE),
                voltage=self.send_read_command(ReadCmds.ETALON_HEATER_DRIVE),
            ),
            brf=GenesisMXTempMetric(
                temp=self.send_read_command(ReadCmds.BRF_TEMPERATURE),
                voltage=self.send_read_command(ReadCmds.BRF_HEATER_DRIVE),
            ),
            shg=GenesisMXTempMetric(
                temp=self.send_read_command(ReadCmds.SHG_TEMPERATURE),
                voltage=self.send_read_command(ReadCmds.SHG_HEATER_DRIVE),
            ),
        )


    @property
    def temperature_c(self):
        """
        Get the main temperature of the laser.

        Description: Measures the temperature of the main thermoelectric cooler (TEC) that regulates the overall
        temperature of the laser head to ensure optimal performance and stability.
        """
        return float(self.send_read_command(ReadCmds.MAIN_TEMPERATURE))

    @property
    def main_tec_drive_v(self):
        """
        Get the main TEC drive voltage of the laser.

        Measures the drive voltage of the main thermoelectric cooler (TEC), which regulates the overall temperature of the laser head.
        """
        return float(self.send_read_command(ReadCmds.MAIN_TEC_DRIVE))

    @property
    def shg_temperature_c(self):
        """
        Get the SHG temperature of the laser in degrees Celsius.

        Measures the temperature of the Second Harmonic Generation (SHG) heater. The SHG heater is crucial for
        maintaining the proper temperature for efficient frequency doubling processes that convert the laser light to the desired wavelength.
        """
        return float(self.send_read_command(ReadCmds.SHG_TEMPERATURE))

    @property
    def shg_heater_drive_v(self):
        """Get the SHG heater drive voltage of the laser."""
        return float(self.send_read_command(ReadCmds.SHG_HEATER_DRIVE))

    @property
    def brf_temperature_c(self):
        """
        Get the BRF temperature of the laser in degrees Celsius.

        Measures the temperature of the Beam Reference Frequency (BRF) heater. The BRF heater is essential for
        maintaining the proper temperature for the frequency reference of the laser.
        """
        return float(self.send_read_command(ReadCmds.BRF_TEMPERATURE))

    @property
    def brf_heater_drive_v(self):
        """Get the BRF heater drive voltage of the laser."""
        return float(self.send_read_command(ReadCmds.BRF_HEATER_DRIVE))

    @property
    def etalon_temperature_c(self):
        """
        Get the etalon temperature of the laser in degrees Celsius.

        Measures the temperature of the etalon heater. The etalon heater is crucial for maintaining the proper
        temperature for the etalon, which is used to stabilize the laser wavelength.
        """
        return float(self.send_read_command(ReadCmds.ETALON_TEMPERATURE))

    @property
    def etalon_heater_drive_v(self):
        """Get the etalon heater drive voltage of the laser."""
        return float(self.send_read_command(ReadCmds.ETALON_HEATER_DRIVE))

    # Commands

    def send_read_command(self, cmd: ReadCmds):
        """Send a read command to the laser."""
        return self.hops.send_command(cmd.value)

    def send_write_command(self, cmd: WriteCmds, value: float = None):
        """Send a write command to the laser."""
        if value is not None:
            self.hops.send_command(f"{cmd.value}{value}")
        else:
            self.send_command(cmd.value)

    def close(self) -> None:
        self.power_setpoint_mw = 0
        self.hops.close()
