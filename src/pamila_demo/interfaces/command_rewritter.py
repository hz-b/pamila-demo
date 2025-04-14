"""convert the values from one state space

Todo:
    Should one have conversion a property name
"""
from abc import ABCMeta, abstractmethod
from typing import Sequence

from ..model.command import Command


class CommandRewriterBase(metaclass=ABCMeta):
    """alternative:
            TranslationService
    """
    @abstractmethod
    def forward(self, command: Command) -> Command:
        raise NotImplementedError("use derived class instead")

    @abstractmethod
    def inverse(self, command: Command) -> Command:
        raise NotImplementedError("use derived class instead")
