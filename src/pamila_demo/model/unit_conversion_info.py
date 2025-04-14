"""

Todo:
    should be moved to an implementation part
"""

from dataclasses import dataclass
from typing import Hashable

from .identifiers import ConversionID
from ..interfaces.lookup_element import LookupElement


@dataclass(frozen=True)
class LinearUnitConversionInfo(LookupElement):
    """
    """
    conversion_id : ConversionID
    intercept: float
    slope: float

    def id(self) -> Hashable:
        return self.conversion_id


@dataclass(frozen=True)
class EnergyIndependentLinearUnitConversionInfo(LookupElement):
    """The name says it"""
    conversion_id : ConversionID
    intercept: float
    slope: float

    def id(self) -> Hashable:
        return self.conversion_id
