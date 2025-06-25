import logging
from typing import Mapping

from pamila_demo.interfaces.liaison_manager import LiaisonManagerBase
from pamila_demo.model.identifiers import LatticeElementPropertyID, DevicePropertyID

logger = logging.getLogger("pamila")



class LiaisonManager(LiaisonManagerBase):
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
            forward_family_lut, Mapping,
            forward_lut: Mapping[LatticeElementPropertyID, DevicePropertyID],
            inverse_lut: Mapping[DevicePropertyID, LatticeElementPropertyID],
        ):
        self.forward_lut = forward_lut
        self.inverse_lut = inverse_lut

    def forward(self, id_: LatticeElementPropertyID) -> DevicePropertyID:
        try:
            return self.forward_lut[id_]
        except KeyError as ke:
            logger.error(f"{self.__class__.__name__} id {id_} not found in lookup table: {ke}")
            raise ke

    def inverse(self, id_: DevicePropertyID) -> LatticeElementPropertyID:
        try:
            return self.inverse_lut[id_]
        except KeyError as ke:
            logger.error(f"{self.__class__.__name__} id {id_} not found in lookup table: {ke}")
            raise ke
