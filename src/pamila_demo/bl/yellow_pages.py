"""

Todo:
    replace with database querries
    consider caching

"""
from enum import Enum
from typing import Sequence, Union

from ..interfaces.yellow_pages import YellowPages


class FamilyName(Enum):
    quadrupoles = "quadrupoles"
    sextupoles = "sextupoles"
    horizontal_steerers = "horizontal_steerers"
    vertical_steerers = "vertical_steerers"
    master_clock = "master_clock"


class YellowPages(YellowPages):
    """

    Todo:
        review if separate methods should be used for
        * horizontal_steerer_names
        * vertical_steerer_names

        or use:
        get(family_name: str)

        separate yellow pages for lattice elements and devices
    """
    def __init__(self, d: dict):
        self._d = d

    def get(self, family_name: Union[str, FamilyName]) -> Sequence[str]:
        # check for valid key?
        # key = str(FamilyName(family_name))
        return self._d[family_name]

    def horizontal_steerer_names(self) -> Sequence[str]:
        return self.get("horizontal_steerers")

    def vertical_steerer_names(self) -> Sequence[str]:
        return self.get("vertical_steerers")

    def quadrupole_names(self) -> Sequence[str]:
        return self.get("quadrupoles")

    def tune_correction_quadrupole_names(self) -> Sequence[str]:
        quads = self.quadrupole_names()
        # Todo: Bessy specific guess
        # should be dedicated field
        return [name for name in quads if name[1] in ["3", "4"]]

    def sextupole_names(self) -> Sequence[str]:
        return self.get("sextupoles")


def yellow_pages_obsolete():
    """
    Todo:
        to be produced by data from database
        or if so from config ...
    """
    raise NotImplementedError("Use build_managers instead")
    # standard quadrupoles
    quadrupoles = [
        f"Q{family}M{child}{sector_type}{sector}R"
        for family in range(1, 6)
        for child in range(1, 3)
        for sector_type in ["D", "T"]
        for sector in range(1, 9)
    ]
    # Emil straight
    quadrupoles += ["QIT6R"]

    sextupoles = [
        f"S{family}M{sector_type}{sector}R"
        for family in range(1, 2)
        for sector_type in ["D", "T"]
        for sector in range(1, 9)
    ]
    sextupoles += [
        f"S{family}M{child}{sector_type}{sector}R"
        for family in range(2, 6)
        for child in range(1, 3)
        for sector_type in ["D", "T"]
        for sector in range(1, 9)
    ]
    horizontal_steerers = [
        f"H{sextupole}" for sextupole in sextupoles if sextupole[1] in ["1", "4"]
    ]
    vertical_steerers = [
        f"V{sextupole}" for sextupole in sextupoles if sextupole[1] in ["2", "3"]
    ]
    d = dict(
        quadrupoles=quadrupoles,
        sextupoles=sextupoles,
        horizontal_steerers=horizontal_steerers,
        vertical_steerers=vertical_steerers,
        master_clock="master_clock",
    )

    return YellowPages(d)
