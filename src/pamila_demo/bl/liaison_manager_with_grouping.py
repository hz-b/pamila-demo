import logging
from dataclasses import dataclass
from functools import cached_property
from typing import Mapping, Sequence

from pamila_demo.interfaces.liaison_manager import LiaisonManagerBase
from pamila_demo.model.identifiers import DevicePropertyID, LatticeElementPropertyID


logger = logging.getLogger("pamila")


@dataclass
class LatticeElementPropertiesLUT:
    element_name: str
    lut: Mapping[str, DevicePropertyID]


@dataclass
class LatticeElementsPropertiesCollection:
    #: used for displaying error or debug infos
    name: str
    col: Sequence[LatticeElementPropertiesLUT]

    def get(self, name) -> LatticeElementPropertiesLUT:
        return self._dict[name]

    @cached_property
    def _dict(self):
        return {elem.element_name: elem for elem in self.col}

@dataclass
class DevicesPropertiesLUT:
    device_name: str
    lut: Mapping[str, LatticeElementPropertyID]


@dataclass
class DevicePropertiesLUTCollection:
    #: used for displaying error or debug infos
    name: str
    col: Sequence[DevicesPropertiesLUT]

    def get(self, name) -> DevicesPropertiesLUT:
        return self._dict[name]

    @cached_property
    def _dict(self):
        return {dev.device_name : dev for dev in self.col}


class LiaisonManagerWithGrouping(LiaisonManagerBase):
    """
    Todo:
        consider internally to represent classes of devices with a certain functionallity

        So internally have
            * classes of devices providing similar properties
            * this can be used when searching for suggesting alternatives to the
              user when searching for it

    """
    def __init__(
            self,
            forward_family_luts: Sequence[LatticeElementsPropertiesCollection],
            inverse_family_luts: Sequence[DevicePropertiesLUTCollection],
            forward_lut: Mapping[LatticeElementPropertyID, DevicePropertyID],
            inverse_lut: Mapping[DevicePropertyID, LatticeElementPropertyID],
        ):
        """
        Todo:
            - build a mapping from element names to family luts?
            - do the same for devices
        """
        self.forward_family_luts = forward_family_luts
        self.inverse_family_luts = inverse_family_luts
        self.forward_lut = forward_lut
        self.inverse_lut = inverse_lut

    def forward(self, id_: LatticeElementPropertyID) -> DevicePropertyID:
        # try families first
        for family_lut in self.forward_family_luts:
            try:
                elem_lut = family_lut.get(id_.element_name)
            except KeyError as ke:
                logger.warning("Could not find key %s in lut %s", id_.element_name, family_lut.name)
                continue

            try:
                r = elem_lut.lut[id_.property]
            except KeyError as ke:
                # remove me ... just a debug entry point
                pass
                raise ke
            return r

        # fall back to stretched out if required
        try:
            return self.forward_lut[id_]
        except KeyError as ke:
            logger.error(f"{self.__class__.__name__} id {id_} not found in lookup table: {ke}")
            raise ke

    def inverse(self, id_: DevicePropertyID) -> LatticeElementPropertyID:
        for family_lut in self.inverse_family_luts:
            try:
                dev_lut = family_lut.get(id_.device_name)
            except KeyError as ke:
                logger.warning("Could not find key %s in lut %s",
                               id_.device_name, family_lut.name)
                continue
            return dev_lut.lut[id_.property]

        try:
            return self.inverse_lut[id_]
        except KeyError as ke:
            logger.error(f"{self.__class__.__name__} id {id_} not found in lookup table: {ke}")
            raise ke
