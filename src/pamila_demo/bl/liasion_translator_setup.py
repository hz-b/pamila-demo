"""
Todo:
    rework to use proper data
"""
import itertools
import logging
from typing import Dict, Sequence

from .liaison_manager import LiaisonManager
from .translator_service import TranslatorService
from .unit_conversion import LinearUnitConversion, EnergyIndependentLinearUnitConversion
from .yellow_pages import yellow_pages
from ..custom.bessyii.constants import ring_parameters, cavity_names
from ..custom.bessyii.querries import get_magnets
from ..interfaces.liaison_manager import LiaisonManagerBase
from ..interfaces.translator_service import TranslatorServiceBase
from ..interfaces.yellow_pages import YellowPages
from ..model.elementmodel import MagnetElementSetup
from ..model.identifiers import DevicePropertyID, LatticeElementPropertyID, ConversionID

logger = logging.getLogger("pamila")


def remove_id(d: Dict) -> Dict:
    nd = d.copy()
    nd.pop("_id", None)
    return nd


def magnet_infos_from_db() -> Sequence[MagnetElementSetup]:
    return [MagnetElementSetup(**remove_id(info)) for info in get_magnets().to_list()]


def element_method(element_name, yp: YellowPages):
    """
    Map an element's family to its property name.

    Args:
        :param element_name: The name of the element.
        :param yp: A YellowPages instance containing families of elements.

    Returns:
        The property name associated with the element's family.

    Raises:
        AssertionError: If the element is not found in any family.
    """
    mapping = {
        "quadrupoles": "K",
        "sextupoles": "H",
        "horizontal_steerers": "x_kick",
        "vertical_steerers": "y_kick",
    }
    for family, prop in mapping.items():
        if element_name in yp.get(family):
            return prop
    raise AssertionError(f"Don't know how to handle {element_name}")


def extract_host_element_name(element_name: str, yp: YellowPages) -> str:
    """
    Extract the host element name for steerers by removing a prefix if applicable.

    Args:
        :param element_name: The original element name.
        :param yp: The YellowPages instance for element families.

    Returns:
        A stripped element name if it belongs to steerers; otherwise, returns the original name.
    """
    if element_name in itertools.chain(yp.get("horizontal_steerers"), yp.get("vertical_steerers")):
        return element_name[1:]
    return element_name


def construct_energy_independent_linear_conversion(
        slope: float,
) -> EnergyIndependentLinearUnitConversion:
    """
    Construct an energy-independent linear conversion using a given slope.

    Args:
        :param slope: The slope to use for conversion.

    Returns:
        An EnergyIndependentLinearUnitConversion instance.

    Raises:
        ValueError: If slope is None.
    """
    if slope is None:
        raise AssertionError("Refusing creating linear unit conversion without slope")
    return EnergyIndependentLinearUnitConversion(
        slope=1.0 / slope, intercept=0.0, brho=ring_parameters.brho
    )


def build_managers(
        yp: YellowPages = yellow_pages(),
) -> (LiaisonManagerBase, TranslatorServiceBase):
    """A first poor mans implementation of liasion manager and Translation service for BessyII

    Todo:
        Which info is already in database and better obtained from database?
    """
    infos = magnet_infos_from_db()

    magnet_types = set([info.type for info in infos])
    # Make sure that names are unique ... everything down the list depends on it
    magnet_names = set([info.name for info in infos])
    if len(list(magnet_names)) != len(infos):
        raise AssertionError(
            "Magnet names seem not to be unique, but is assumption of all further processing"
        )

    power_converter_names = set([info.pc for info in infos])
    power_converter_feeds = {
        pc_name: [info.name for info in infos if info.pc == pc_name]
        for pc_name in power_converter_names
    }

    # todo: check if property must be different for the different magnets ...

    # first for steerers : for AT these are angles applied to the host magnet
    # I use that I know one pc goes to one steerer
    inverse_lut = {
        DevicePropertyID(device_name=info.pc, property="set_current"):
            LatticeElementPropertyID(element_name=info.name[1:], property="x_kick")
        for info in infos
        if info.name in yp.horizontal_steerer_names()
    }
    inverse_lut.update(
        {
            DevicePropertyID(device_name=info.pc, property="set_current"):
                LatticeElementPropertyID(element_name=info.name[1:], property="y_kick")
            for info in infos
            if info.name in yp.vertical_steerer_names()
        }
    )

    # steerers ... direct kick
    forward_lut = {
        LatticeElementPropertyID(element_name=info.name[1:], property="x_kick"):
            DevicePropertyID(device_name=info.pc, property="set_current")
        for info in infos
        if info.name in yp.horizontal_steerer_names()
    }
    forward_lut.update({
        LatticeElementPropertyID(element_name=info.name[1:], property="y_kick"):
            DevicePropertyID(device_name=info.pc, property="set_current")
        for info in infos
        if info.name in yp.vertical_steerer_names()
    })
    # steerers ... kick relative to the already set one
    forward_lut = {
        LatticeElementPropertyID(element_name=info.name[1:], property="delta_x_kick"):
            DevicePropertyID(device_name=info.pc, property="delta_set_current")
        for info in infos
        if info.name in yp.horizontal_steerer_names()
    }
    forward_lut.update({
        LatticeElementPropertyID(element_name=info.name[1:], property="delta_y_kick"):
            DevicePropertyID(device_name=info.pc, property="delta_set_current")

        for info in infos
        if info.name in yp.vertical_steerer_names()
    })
    # Test that steerer power converters only feed one before going to the next step
    for key in inverse_lut:
        corr_pc = key.device_name
        magnet_names = power_converter_feeds[corr_pc]
        if len(magnet_names) != 1:
            raise AssertionError(
                f"Found {magnet_names} magnets on assumed corrector power supply {corr_pc}"
            )

    forward_lut.update(
        {
            LatticeElementPropertyID(element_name="master_clock", property="delta_frequency"):
                DevicePropertyID(device_name="master_clock", property="delta_frequency")
        }
    )
    # quadrupoles and sextupoles
    steerer_pc_names = [key.device_name for key in inverse_lut]
    # inverse_lut.update(
    #     {
    #         DevicePropertyID(device_name=pc_name, property="set_current"):
    #             LatticeElementPropertyID(element_name=magnet_name, property="K")
    #         for magnet_name in magnet_names
    #         if magnet_name in yp.quadrupole_names()
    #         for pc_name, magnet_names in power_converter_feeds.items()
    #         if pc_name not in steerer_pc_names
    #     }
    # )
    # inverse_lut.update(
    #     {
    #         DevicePropertyID(device_name=pc_name, property="set_current"):
    #             LatticeElementPropertyID(element_name=magnet_name, property="H")
    #         for magnet_name in magnet_names
    #         if magnet_name in yp.sextupole_names()
    #         for pc_name, magnet_names in power_converter_feeds.items()
    #         if pc_name not in steerer_pc_names
    #     }
    # )

    # inverse_lut.update(
    #     {
    #         DevicePropertyID(device_name=pc_name, property="set_current"): tuple(
    #             [
    #                 LatticeElementPropertyID(
    #                     element_name=magnet_name, property="main_strength"
    #                 )
    #                 for magnet_name in magnet_names
    #             ]
    #         )
    #         for pc_name, magnet_names in power_converter_feeds.items()
    #         if pc_name not in steerer_pc_names
    #     }
    # )

    # Add lut for quadrupoles and sextupole
    # Furthermore to feed through the K value ...
    # Todo:
    #     is that appropriate ?
    #     Should one rather use a handler for lattice elements
    quad_updates = dict()
    for axis_name in "x", "y":
        quad_updates.update(
            {
                DevicePropertyID(device_name=info.name, property=axis_name):
                    LatticeElementPropertyID(
                        element_name=info.name, property=axis_name
                    )
                for info in infos
                if info.type in ["Sextupole", "Quadrupole"]
            }
        )
    inverse_lut.update(quad_updates)

    # Cavities and master clock
    inverse_lut.update(
        {
            DevicePropertyID(device_name=name, property="frequency"): (
                LatticeElementPropertyID(element_name=name, property="frequency"),
            )
            for name in cavity_names
        }
    )
    inverse_lut.update(
        {
            DevicePropertyID(
                device_name="master_clock", property="reference_frequency"
            ): tuple(
                [
                    LatticeElementPropertyID(element_name=name, property="frequency")
                    for name in cavity_names
                ]
            )
        }
    )

    lm = LiaisonManager(forward_lut=forward_lut, inverse_lut=inverse_lut)

    # start to build it for the magnets ... power converter feed
    translator_lut = {
        ConversionID(
            LatticeElementPropertyID(
                element_name=extract_host_element_name(info.name, yp=yp),
                property=element_method(info.name, yp=yp),
            ),
            DevicePropertyID(device_name=info.pc, property="set_current"),
        ):
        # todo: check for the correct conversion
            construct_energy_independent_linear_conversion(slope=info.magnetic_strength)
        for info in infos
    }
    # add difference for correctors ....
    # todo: can be that this step requires connection to the machine
    #       let's try it now and see if it is acceptable for correctors ?
    #
    translator_lut = {
        ConversionID(
            LatticeElementPropertyID(
                element_name=extract_host_element_name(info.name, yp=yp),
                property="delta_" + element_method(info.name, yp=yp),
            ),
            DevicePropertyID(device_name=info.pc, property="delta_set_current"),
        ):
        # todo: check for the correct conversion
            construct_energy_independent_linear_conversion(slope=info.magnetic_strength)
        for info in infos if info.name in itertools.chain(yp.get("horizontal_steerers"), yp.get("vertical_steerers"))
    }

    # add look up for value using main strength for quadrupoles and sextupoles
    translator_lut.update(
        {
            ConversionID(
                LatticeElementPropertyID(
                    element_name=extract_host_element_name(info.name, yp=yp),
                    property="main_strength",
                ),
                DevicePropertyID(device_name=info.pc, property="set_current"),
            ):
            # todo: check for the correct conversion
                construct_energy_independent_linear_conversion(slope=info.magnetic_strength)
            for info in infos
            if info.type in ["Sextupole", "Quadrupole"]
        }
    )
    # should this conversion really be energy independent ?

    translator_lut.update({
        ConversionID(
            LatticeElementPropertyID(element_name="master_clock", property="delta_frequency"),
            DevicePropertyID(device_name="master_clock", property="delta_frequency")
        ): LinearUnitConversion(slope=1, intercept=0)
    })
    axis_updates = dict()
    # start to build it for quadrupoles and sextupoles axes
    for axis_name in "x", "y":
        axis_updates.update(
            {
                ConversionID(
                    lattice_property_id=LatticeElementPropertyID(
                        element_name=info.name, property=axis_name
                    ),
                    device_property_id=DevicePropertyID(
                        device_name=info.name, property=axis_name
                    ),
                ): LinearUnitConversion(slope=1.0, intercept=0.0)
                for info in infos
                if info.type in ["Sextupole", "Quadrupole"]
            }
        )
    translator_lut.update(axis_updates)

    # K and H as requested from the device world ... should it be there?
    # translator_lut.update(
    #     {
    #         ConversionID(
    #             lattice_property_id=LatticeElementPropertyID(
    #                 element_name=info.name, property="K"
    #             ),
    #             device_property_id=DevicePropertyID(
    #                 device_name=info.name, property="K"
    #             ),
    #         ): LinearUnitConversion(slope=1.0, intercept=0.0)
    #         for info in infos
    #         if info.type in ["Quadrupole"]
    #     }
    # )
    # Todo: questionable if that should be handled here ...
    # view should know what to delegate to the lattice
    # translator_lut.update(
    #     {
    #         ConversionID(
    #             lattice_property_id=LatticeElementPropertyID(
    #                 element_name=info.name, property="H"
    #             ),
    #             device_property_id=DevicePropertyID(
    #                 device_name=info.name, property="H"
    #             ),
    #         ): LinearUnitConversion(slope=1.0, intercept=0.0)
    #         for info in infos
    #         if info.type in ["Sextupole"]
    #     }
    # )

    # cavities
    translator_lut.update(
        {
            ConversionID(
                lattice_property_id=LatticeElementPropertyID(
                    element_name=name, property="frequency"
                ),
                device_property_id=DevicePropertyID(
                    device_name=name, property="frequency"
                ),
            ): LinearUnitConversion(
                slope=1e-3, intercept=0.0
            )  # BESSY II uses kHz for the cavities clock
            for name in cavity_names
        }
    )

    translator_lut.update(
        {
            ConversionID(
                LatticeElementPropertyID(element_name=name, property="frequency"),
                DevicePropertyID(
                    device_name="master_clock", property="reference_frequency"
                ),
            ): LinearUnitConversion(
                slope=1e-3, intercept=0.0
            )  # BESSY II uses kHz for the master clock
            for name in cavity_names
        }
    )

    tm = TranslatorService(translator_lut)
    return lm, tm


if __name__ == "__main__":
    build_managers()
