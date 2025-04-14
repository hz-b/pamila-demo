from .liasion_translator_setup import build_managers
from ..bl.command_rewritter import CommandRewriter


def set_command_rewriter():
    lm, tm = build_managers()
    return CommandRewriter(liaison_manager=lm, translation_service=tm, )