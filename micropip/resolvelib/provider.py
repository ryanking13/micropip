from collections.abc import Sequence
from functools import lru_cache
from typing import Any, Iterator, Mapping, override
from .._vendored.resolvelib.src.resolvelib import AbstractProvider
from .._vendored.packaging.src.packaging.requirements import Requirement
from .._vendored.packaging.src.packaging.utils import canonicalize_name
from .candidate import BaseCandidate, PyPICandidate, LockfileCandidate
# from .base import Requirement, Candidate


class MicropipProvider(AbstractProvider):
    """Provider Implementation for resolvlib"""

    def __init__(
        self,
        search_pyodide_lock_first: bool = True,
    ):
        # Whether to search PyPI first or lockfile first
        self._search_pyodide_lock_first = search_pyodide_lock_first

    @override
    def identify(self, requirement_or_candidate: Requirement | BaseCandidate):
        return canonicalize_name(requirement_or_candidate.name)

    # def get_extras_for(self, requirement_or_candidate):
    #     # Extras is a set, which is not hashable
    #     return tuple(sorted(requirement_or_candidate.extras))

    # def get_base_requirement(self, candidate):
    #     return Requirement(f"{candidate.name}=={candidate.version}")

    @override
    def get_preference(
        self,
        identifier: str,
        resolutions: Mapping[str, BaseCandidate],
        candidates: Mapping[str, Iterator[BaseCandidate]],
        information: Any,  # doesn't care for now
        backtrack_causes: Sequence[Any],  # doesn't care for now
    ):
        """
        The preference is defined as
        "I think this requirement should be resolved first"

        We don't care about this for now, so we just use the example value from resolvelib.
        """
        return sum(1 for _ in candidates[identifier])

    @override
    def find_matches(
        self,
        identifier: str,
        requirements: Mapping[str, Iterator[Requirement]],
        incompatibilities: Mapping[str, Iterator[BaseCandidate]],
    ):
        requirements = list(requirements[identifier])
        assert not any(
            r.extras for r in requirements
        ), "extras not supported in this example"

        bad_versions = {c.version for c in incompatibilities[identifier]}

        # TODO:
        # based on whether to search PyPI or lockfile.
        # return the iterator that yields the candidates to make sure extra http calls are not made

        # # Need to pass the extras to the search, so they
        # # are added to the candidate at creation - we
        # # treat candidates as immutable once created.
        # candidates = (
        #     candidate
        #     for candidate in get_project_from_pypi(identifier, set())
        #     if candidate.version not in bad_versions
        #     and all(candidate.version in r.specifier for r in requirements)
        # )
        # return sorted(candidates, key=attrgetter("version"), reverse=True)

    @override
    @lru_cache(maxsize=None)
    def is_satisfied_by(self, requirement: Requirement, candidate: BaseCandidate):
        if canonicalize_name(requirement.name) != candidate.name:
            return False

        return requirement.specifier.contains(candidate.version, prereleases=True)

    # @override
    # def get_dependencies(self, candidate: Candidate) -> Sequence[Requirement]:
    #     with_requires = not self._ignore_dependencies
    #     return [r for r in candidate.iter_dependencies(with_requires) if r is not None]

    @override
    def get_dependencies(self, candidate):
        return candidate.dependencies