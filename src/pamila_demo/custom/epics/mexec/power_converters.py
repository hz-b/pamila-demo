import asyncio

from typing_extensions import Unpack

from bact_bessyii_mls_ophyd.devices.utils.multiplexer_for_settable_devices import _MultiplexerItemProxy
from bact_bessyii_mls_ophyd.devices.utils.power_converter import PowerConverter as _PowerConverter

from bluesky.protocols import Movable, Stoppable, Stageable, T_co, Status

from ophyd_async.core import (
    AsyncStatus,
    StandardReadable,
    SignalR,
    SignalRW,
    observe_value,
    WatcherUpdate,
    WatchableAsyncStatus
)


class NotInitalisedReferenceValue(AssertionError):
    """reference value not installed"""


class DiffCurrent(StandardReadable, Movable):
    def __init__(self, *, name, parent):
        super().__init__(name=name)
        self.reference_value = None
        self.parent = parent

    @AsyncStatus.wrap
    async def stage(self):
        r = await super().stage()
        # Todo ... mangle it ...
        self.reference_value = await self.parent.setpoint.get_value()
        return r

    @AsyncStatus.wrap
    async def unstage(self):
         stat = await super().unstage()
         self.reference_value = None
         return stat

    @AsyncStatus.wrap
    async def set(self, diff_value) -> Status:
        assert self.reference_value is not None
        value = diff_value + self.reference_value
        return super().set(value)


class MultiplexerItemProxy(_MultiplexerItemProxy):
    pass

    # def __init__(self, **kwargs):
    #     with self.add_children_as_readables():
    #        self.delta_set_current = DiffCurrent(parent=self)
    #    super().__init__(**kwargs)

class PowerConverter(_PowerConverter):

    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.delta_set_current = DiffCurrent(parent=self, name=f"{kwargs['name']}-diff-current")
        super().__init__(*args, **kwargs)

