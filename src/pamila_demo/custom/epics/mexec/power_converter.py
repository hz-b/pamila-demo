from bact_bessyii_mls_ophyd.devices.utils.multiplexer_for_settable_devices import (
    _MultiplexerItemProxy,
)
from bact_bessyii_mls_ophyd.devices.utils.pv_positioner_like_utils import PVPositionerIsClose
from .diff_channel import DiffChannel



class MultiplexerItemProxy(_MultiplexerItemProxy):
    """
    Todo:
        need to provide difference current
    """

    pass


class PowerConverter(PVPositionerIsClose):
    def __init__(self, *args, **kwargs):
        with self.add_children_as_readables():
            self.delta_set_current = DiffChannel(
                parent=self, name=f"{kwargs['name']}-diff-current"
            )
        super().__init__(*args, **kwargs)
