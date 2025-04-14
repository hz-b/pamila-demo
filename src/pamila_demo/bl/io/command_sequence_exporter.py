import json
from typing import Sequence
from dataclasses import asdict
import jsons

from ...model.command import CommandSequence, Command


def commands_to_json(commands: Sequence[Command]):
    return jsons.dump(asdict(CommandSequence(commands=commands)))

def export_commands(commands: Sequence[Command], fp):
    json.dump(commands_to_json(commands=commands), fp, indent=2)