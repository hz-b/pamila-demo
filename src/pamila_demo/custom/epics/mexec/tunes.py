from ophyd_async.core import StandardReadable
from ophyd_async.epics.core import epics_signal_r


class TuneSignal(StandardReadable):
    def __init__(self, prefix, *, name: str):
        with self.add_children_as_readables():
            self.sig = epics_signal_r(float, f"{prefix}:tune")
        super().__init__(name=name)

    async def read(self):
        # Wait for new tune data to arrive
        async with self.sig.subscribe() as updates:
            async for value in updates:
                break
        return super().read()


class Tunes(StandardReadable):
    def __init__(self, prefix, *, name):
        with self.add_children_as_readables():
            self.x = TuneSignal(f"{prefix}:x", name=f"{name}-x")
            self.y = TuneSignal(f"{prefix}:x", name=f"{name}-y")
        super().__init__(name=name)
