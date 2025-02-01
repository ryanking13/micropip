"""
Reporter class implementation for resolvelib.
"""
from typing import Any
from ..logging import setup_logging
from .._vendored.resolvelib.src.resolvelib import BaseReporter
from .base import Requirement, Candidate

class DebuggingReporter(BaseReporter):
    """
    Adapted from pip.

    A reporter that does an info log for every event it sees.
    """
    def __init__(self, verbose) -> None:
        self._ctx = setup_logging().ctx_level(verbose)
        self._logger = self._ctx.__enter__()

    def __del__(self) -> None:
        self._ctx.__exit__(None, None, None)

    def starting(self) -> None:
        self.logger.info("Reporter.starting()")

    def starting_round(self, index: int) -> None:
        self.logger.info("Reporter.starting_round(%r)", index)

    def ending_round(self, index: int, state: Any) -> None:
        self.logger.info("Reporter.ending_round(%r, state)", index)
        self.logger.debug("Reporter.ending_round(%r, %r)", index, state)

    def ending(self, state: Any) -> None:
        self.logger.info("Reporter.ending(%r)", state)

    def adding_requirement(self, requirement: Requirement, parent: Candidate) -> None:
        self.logger.info("Reporter.adding_requirement(%r, %r)", requirement, parent)

    def rejecting_candidate(self, criterion: Any, candidate: Candidate) -> None:
        self.logger.info("Reporter.rejecting_candidate(%r, %r)", criterion, candidate)

    def pinning(self, candidate: Candidate) -> None:
        self.logger.info("Reporter.pinning(%r)", candidate)
