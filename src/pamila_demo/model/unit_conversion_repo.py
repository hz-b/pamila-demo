from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple, Union
from .unit_conversion_info import LinearUnitConversionInfo
from .identifiers import LatticeElementPropertyID, DevicePropertyID


@dataclass(frozen=True)
class UnitConversionRepo:
    """

    Todo:
       should it derive from some interface?
    """

    conversion_info: Tuple[LinearUnitConversionInfo]

    @lru_cache(maxsize=1)
    def _lookup_table(self):
        lut = dict()
        def add_entry(identifer, item):
            if identifer.known():
                lut.update({identifer : item })
        for item in self.conversion_info:
            add_entry(item.conversion_id.lattice_property_id, item)
            add_entry(item.conversion_id.device_property_id, item)
        return lut

    def get(self, id_: Union[LatticeElementPropertyID, DevicePropertyID]):
        """
        Todo:
            should this method be an overload of an abstract method?
        """
        return self._lookup_table()[id_]
