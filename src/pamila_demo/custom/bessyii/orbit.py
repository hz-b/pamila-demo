import logging
from typing import Annotated as A, Sequence, Dict

import numpy as np
from bluesky.protocols import Reading
from event_model import DataKey
from ophyd_async.core import SignalR, StandardReadable, Array1D, AsyncStatus
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.epics.core import EpicsDevice, PvSuffix

from ...model.orbit import Orbit as OrbitModel, BPMReading, BPMPosition, BPMButtons

logger = logging.getLogger("pamila-demo")


class Orbit(StandardReadable, EpicsDevice):
    # fmt:off
    names: A[ SignalR[ Sequence[str]       ], PvSuffix( "rdBpmNames" ), Format.CONFIG_SIGNAL   ]

    count: A[ SignalR[ int                 ], PvSuffix( "count"      ), Format.UNCACHED_SIGNAL ]

    rpos:  A[ SignalR[ Array1D[np.float64] ], PvSuffix( "rdPos"      ), Format.UNCACHED_SIGNAL ]
    btns:  A[ SignalR[ Array1D[np.float64] ], PvSuffix( "rdButtons"  ), Format.UNCACHED_SIGNAL ]
    # fmt:on

    @AsyncStatus.wrap
    async def read(self) -> dict[str, Reading]:
        cnt = await self.count.get_value(cached=False)
        logger.warning("New orbit count r = %s", cnt)
        return await super().read()


class PPOrbit(Orbit):
    """Provide read in data as orbit model"""

    async def describe(self) -> dict[str, DataKey]:
        d = await super().describe()
        d.pop(f"{self.name}-btns")
        rpos = d.pop(f"{self.name}-rpos")
        L, = rpos["shape"]
        assert L % 2 == 0
        d2 = {f"{self.name}-pos" : DataKey(source="", shape=[L//2], dtype="array")}
        d.update(d2)
        return d

    async def read(self) -> Dict[str, Reading]:
        data = await super().read()
        # todo: has ophyd / bluesky a helper func for splitting the read data?
        pos_pkg = data.pop(f"{self.name}-rpos")
        btn_pkg = data.pop(f"{self.name}-btns")
        pos = np.reshape(pos_pkg["value"], (-1, 2))
        btns = np.reshape(btn_pkg["value"], (-1, 4))
        names = await self.names.get_value()
        pos = {
            f"{self.name}-pos": Reading(
                timestamp=pos_pkg["timestamp"],
                value=OrbitModel(
                    orbit=[
                        BPMReading(
                            name=name,
                            pos=BPMPosition(x=p[0], y=p[1]),
                            btns=BPMButtons(*b),
                        )
                        for name, p, b in zip(names, pos, btns)
                    ]
                ).to_json(),
            )
        }
        data.update(pos)
        return data


if __name__ == "__main__":
    import asyncio

    orbit = Orbit("ORBITCC:", name="orb")

    async def test():
        await orbit.connect()
        r = await orbit.read()
        print(r)

    asyncio.run(test())
