import itertools

from pamila_demo.bl.yellow_pages import yellow_pages
from src.pamila_demo.model.command import BehaviourOnError, Command
from src.pamila_demo.bl.io.command_sequence_exporter import export_commands

# from bact_twin_architecture.data_model.command import Command, BehaviourOnError

# from bact_twin_bessyii_impl.bl.bessyii_yellow_pages import bessyii_yellow_pages
# from bact_twin_bessyii_impl.bl.io.command_sequence_exporter import export_commands

yp = yellow_pages()

#todo: provided by client
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
