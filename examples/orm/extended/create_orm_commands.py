import itertools

from pamila_demo.bl.io.command_sequence_exporter import export_commands
from pamila_demo.bl.liasion_translator_setup import load_managers
from pamila_demo.model.command import BehaviourOnError, Command

yp, _, __  = load_managers()

# todo: provided by client
measurement_values = [0, 1e-5, 0, -1e-5, 0]
commands = [
    Command(
        id=corr, property="delta_y_kick", value=val, behaviour_on_error=BehaviourOnError.stop
    )
    for corr, val in itertools.product([name[1:] for name in yp.vertical_steerer_names()], measurement_values)
]
commands += [
    Command(
        id=corr, property="delta_x_kick", value=val, behaviour_on_error=BehaviourOnError.stop
    )
    for corr, val in itertools.product([name[1:] for name in yp.horizontal_steerer_names()], measurement_values)
]
with open("orm_commands.json", "wt") as fp:
    export_commands(commands, fp)
