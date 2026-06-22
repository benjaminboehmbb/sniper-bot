from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_result import ScientificResult


InputT = TypeVar("InputT", bound=ScientificObject)
ResultT = TypeVar("ResultT", bound=ScientificResult)


class ScientificProcessor(ABC, Generic[InputT, ResultT]):
    """
    Abstract base class for deterministic SSI scientific processors.

    A processor transforms a scientific input object into a scientific result.

    Required lifecycle:

    validate_input
    -> process
    -> ScientificResult

    Processors must not perform execution behavior, live trading decisions
    or hidden side effects.
    """

    @abstractmethod
    def validate_input(self, input_object: InputT) -> None:
        pass

    @abstractmethod
    def process(self, input_object: InputT) -> ResultT:
        pass