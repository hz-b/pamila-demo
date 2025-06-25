from typing import List

from bact_bessyii_mls_ophyd.devices.utils.pv_positioner_like_utils import (
    PVPositionerIsClose,
)
from .diff_channel import DiffChannel
from bluesky.protocols import Movable, Status
from ophyd_async.core import AsyncStatus, StandardReadable


class MasterClock(StandardReadable):
    """
    Warning:
            This code is not yet tested!
    """

    def __init__(self, prefix, name: str = "", *, eps_rel=1e-6, eps_abs=1):
        with self.add_children_as_readables():
            self.frequency = PVPositionerIsClose(
                prefix, name="f{name}-freq", setpoint_suffix="freq", readback_suffix="freq", eps_abs=eps_abs, eps_rel=eps_rel
            )
            self.delta_frequency = DiffChannel(
                parent=self, name="f{name}-{delta_freq} "
            )
        super().__init__(name=name)
        self.set_frequency_at_start = None

    async def stage(self):
        r = await super().stage()
        self.set_frequency_at_start = await self.frequency.setpoint.read_value()
        return r

    def unstage(self) -> List[object]:
        """

        Todo:
            shall one reset the value to the start current?
        """
        return super().unstage()
