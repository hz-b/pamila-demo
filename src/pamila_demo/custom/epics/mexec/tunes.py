from ophyd_async.core import StandardReadable, AsyncStatus
from ophyd_async.epics.core import epics_signal_r


class TuneSignal(StandardReadable):
    def __init__(self, prefix, *, name: str):
        with self.add_children_as_readables():
            self.sig = epics_signal_r(float, f"{prefix}:tune")
        super().__init__(name=name)

    @AsyncStatus.wrap
    async def read(self):
        # Wait for new tune data to arrive
        await self.sig.get_value(cached=False)
        return await super().read()


class Tunes(StandardReadable):
    def __init__(self, prefix, *, name):
        with self.add_children_as_readables():
            self.x = TuneSignal(f"{prefix}:x", name=f"{name}-x")
            self.y = TuneSignal(f"{prefix}:x", name=f"{name}-y")
        super().__init__(name=name)
