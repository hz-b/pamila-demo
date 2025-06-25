from typing import List

from ophyd import (
    Component as Cpt,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    PVPositionerPC,
    Signal,
)


class MasterClockDiffFrequency(Device):
    """
    todo: same apprache as steerer delta current
          merge
    """

    def set(self, diff_value):
        value = self.parent.set_frequency_at_start.get() + diff_value
        print(f"Setting frequncy to {value}: diff {diff_value}")
        return self.parent.frequency.set(value)


class MasterClockFrequency(PVPositionerPC):
    setpoint = Cpt(EpicsSignal, ":freq")
    readback = Cpt(EpicsSignalRO, ":freq")


class MasterClock(Device):
    frequency = Cpt(MasterClockFrequency, "", name="freq")
    delta_frequency = Cpt(MasterClockDiffFrequency, suffix="", name="delta_freq")
    set_frequency_at_start = Cpt(Signal, name="at_start")

    def stage(self) -> List[object]:
        r = super().stage()
        self.set_frequency_at_start.put(self.frequency.setpoint.get())
        return r

    def unstage(self) -> List[object]:
        """

        Todo:
            shall one reset the value to the start current?
        """
        return super().unstage()
