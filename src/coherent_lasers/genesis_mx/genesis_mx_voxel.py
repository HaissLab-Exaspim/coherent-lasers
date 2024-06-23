from .genesis_mx import GenesisMX
from .commands import OperationModes
from voxel.devices.lasers import BaseLaser

INIT_POWER_MW = 10.0


class GenesisMXVoxelLaser(BaseLaser):
    def __init__(self, id: str, conn: str):
        super.__init(self, id)
        self._inst = GenesisMX(serial=conn)
        try:
            assert self._inst.head['serial'] == conn
        except AssertionError:
            raise ValueError(f'Error initializing laser {self.id}, serial number mismatch')
        self._inst.mode = OperationModes.PHOTO
        self.enable()
        self.power_mw = INIT_POWER_MW

    def enable(self):
        self._inst.enable()

    def disable(self):
        self._inst.disable()

    @property
    def power_mw(self):
        return self._inst.power_mw

    @power_mw.setter
    def power_mw(self, value: float):
        self._inst.power_mw = value

    @property
    def power_setpoint_mw(self):
        return self._inst.power_setpoint_mw

    @property
    def signal_temperature_c(self) -> float:
        """The temperature of the laser in degrees Celsius."""
        return self._inst.temperature_c

    @property
    def modulation_mode(self) -> str:
        return ''

    @modulation_mode.setter
    def modulation_mode(self, value: str):
        pass

    def status(self):
        """Get the status of the laser."""
        pass

    def cdrh(self):
        pass
