
import logging

from pamila_demo.interfaces.state_conversion import StateConversion

logger = logging.getLogger("bact-twin-architecture")


class UnitConversion(StateConversion):
    """a one dimensional conversion"""


class LinearUnitConversion(UnitConversion):
    """uses linear polynom.

    Warning:
        inverse will fail for slopes of 0
    """

    def __init__(self, *, intercept: float, slope: float):
        self.intercept = intercept
        self.slope = slope

    def forward(self, state: float) -> float:
        return self.intercept + self.slope * state

    def inverse(self, state: float) -> float:
        return (state - self.intercept) / self.slope


class EnergyIndependentLinearUnitConversion(StateConversion):
    """Typical example: magnet parameters

    Todo:
        Handle separately if brho changes
    """
    def __init__(self, *, intercept: float, slope: float, brho: float):
        self.intercept = intercept
        self.slope = slope
        self.brho = brho

    def forward(self, state: float) -> float:
        logger.info("%s.forward: brho %s, intercept %s slope %s, state %s", self.__class__.__name__, self.brho, self.intercept, self.slope, state)
        intercept = self.intercept * self.brho
        slope = self.slope * self.brho
        return intercept + slope * state

    def inverse(self, state: float) -> float:
        logger.info("%s.inverse: brho %s, intercept %s slope %s, state %s", self.__class__.__name__, self.brho, self.intercept, self.slope, state)
        intercept = self.intercept * self.brho
        slope = self.slope * self.brho
        return (state - intercept) / slope
