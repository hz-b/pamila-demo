"""
"""
import asyncio
from typing import Sequence

from bact_bessyii_mls_ophyd.devices.utils.multiplexer_for_settable_devices import (
    MultiplexerProxy,
)

# currently in an other package: could be distributed here too
from bact_bessyii_ophyd.devices.pp.bpm.bpm import BPM
from bact_bessyii_ophyd.devices.raw.tune import Tunes
from .master_clock import MasterClock
from ...bessyii.constants import special_pvs
from ....bl.liasion_translator_setup import load_managers
from .power_converters import PowerConverter, MultiplexerItemProxy


def setup(device_ids: Sequence[str], prefix="Anonym:"):
    """

    device_ids: to cross check if device ids are instantiated

    Todo:
        do we need it here ?

    Todo:
        * retrieve steerer names from some service
        * use this a factory for creating the device (stubs) that we need later on

    """
    yp, _, __ = load_managers()

    quad_pcs = {
        name: PowerConverter(
            f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set"
        )
        for name in yp.get("quadrupole_pcs")
    }

    sext_pcs = {
        name: PowerConverter(
            f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set"
        )
        for name in yp.get("sextupole_pcs")
    }

    hor_steerer_pcs = {
        name: PowerConverter(
            f"{prefix}{name}:", name=name, readback_suffix="rdbk", setpoint_suffix="set"
        )
        for name in yp.get("horizontal_steerer_pcs")
    }
    vert_steerer_pcs = {
        name.lower(): PowerConverter(
            f"{prefix}{name}:",
            name=name.lower(),
            readback_suffix="rdbk",
            setpoint_suffix="set",
        )
        for name in yp.get("vertical_steerer_pcs")
    }
    steerer_pcs = hor_steerer_pcs.copy()
    steerer_pcs.update(vert_steerer_pcs)

    quadrupoles = MultiplexerProxy(
        name="quad_col", settable_devices=quad_pcs, default_name=list(quad_pcs)[0]
    )
    sextupoles = MultiplexerProxy(
        name="sext_col", settable_devices=sext_pcs, default_name=list(sext_pcs)[0]
    )
    steerers = MultiplexerProxy(
        name="st_col",
        settable_devices=steerer_pcs,
        default_name=list(steerer_pcs)[0],
        ItemProxy=MultiplexerItemProxy,
    )

    bpms = BPM(f"{prefix}MDIZ2T5G", name="bpm")
    master_clock = MasterClock(f'{prefix}{special_pvs["master_clock"]}', name="mc")
    tunes = Tunes(f"{prefix}beam:twiss", name="tune")
    return dict(
        bpms=bpms,
        steerer_pcs=steerers,
        master_clock=master_clock,
        quadrupole_pcs=quadrupoles,
        sextupoles_pcs=sextupoles,
        tunes=tunes,
    )


__all__ = ["Steerer", "SteererCurrent"]
