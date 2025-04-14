import json

from pamila_demo.bl.command_rewritter import CommandRewriter
from pamila_demo.bl.io.command_sequence_exporter import export_commands
from pamila_demo.bl.liasion_translator_setup import build_managers
from pamila_demo.model.command import CommandSequence, Command


def main():

    lm, tm = build_managers()
    command_rewritter = CommandRewriter(liaison_manager=lm, translation_service=tm)
    # load the commands that operate in lattice space and transform
    # them to machine state
    with open("orm_commands.json") as fp:
        tmp = json.load(fp)

    cmds_on_lattice = CommandSequence(commands=[Command(**d) for d in tmp["commands"]])
    cmds_on_machine = CommandSequence(
        commands=[
            command_rewritter.forward(cmd) for cmd in cmds_on_lattice.commands
        ]
    )
    with open("orm_commands_dev_view.json", "wt") as fp:
        export_commands(cmds_on_machine.commands, fp)


if __name__ == "__main__":
    main()
