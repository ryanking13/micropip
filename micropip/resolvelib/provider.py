from collections.abc import Sequence
from functools import lru_cache
from typing import Iterable, Iterator, Mapping, Union, override
from .._vendored.resolvelib.src.resolvelib import AbstractProvider
from .base import Requirement, Candidate


class MicropipProvider(AbstractProvider):
    """Provider Implementation for resolvlib"""

    def __init__(
        self,
        ignore_dependencies: bool,
        user_requested: dict[str, int],
    ) -> None:
        self._ignore_dependencies = ignore_dependencies
        self._user_requested = user_requested

    @override
    def identify(self, requirement_or_candidate: Requirement | Candidate) -> str:
        return requirement_or_candidate.name

    @override
    def get_preference(
        self,
        identifier: str,
        resolutions: Mapping[str, Candidate],
        candidates: Mapping[str, Iterator[Candidate]],
        information: Mapping[str, Iterable["PreferenceInformation"]],
        backtrack_causes: Sequence["PreferenceInformation"],
    ) -> "Preference":
        """Produce a sort key for given requirement based on preference.

        The lower the return value is, the more preferred this group of
        arguments is.

        Currently micropip considers the following in order:

        * if the requirement exists in the lockfile, and the index url is the default index url,
          then prefer the lockfile candidate.
        * otherwise, lookup teh candidate from the index.
        """
        # try:
        #     next(iter(information[identifier]))
        # except StopIteration:
        #     # There is no information for this identifier, so there's no known
        #     # candidates.
        #     has_information = False
        # else:
        #     has_information = True

        # if has_information:
        #     lookups = (r.get_candidate_lookup() for r, _ in information[identifier])
        #     candidate, ireqs = zip(*lookups)
        # else:
        #     candidate, ireqs = None, ()

        # operators = [
        #     specifier.operator
        #     for specifier_set in (ireq.specifier for ireq in ireqs if ireq)
        #     for specifier in specifier_set
        # ]

        # direct = candidate is not None
        # pinned = any(op[:2] == "==" for op in operators)
        # unfree = bool(operators)

        # try:
        #     requested_order: Union[int, float] = self._user_requested[identifier]
        # except KeyError:
        #     requested_order = math.inf
        #     if has_information:
        #         parent_depths = (
        #             self._known_depths[parent.name] if parent is not None else 0.0
        #             for _, parent in information[identifier]
        #         )
        #         inferred_depth = min(d for d in parent_depths) + 1.0
        #     else:
        #         inferred_depth = math.inf
        # else:
        #     inferred_depth = 1.0
        # self._known_depths[identifier] = inferred_depth

        # requested_order = self._user_requested.get(identifier, math.inf)

        # # Requires-Python has only one candidate and the check is basically
        # # free, so we always do it first to avoid needless work if it fails.
        # requires_python = identifier == REQUIRES_PYTHON_IDENTIFIER

        # # Prefer the causes of backtracking on the assumption that the problem
        # # resolving the dependency tree is related to the failures that caused
        # # the backtracking
        # backtrack_cause = self.is_backtrack_cause(identifier, backtrack_causes)

        # return (
        #     not requires_python,
        #     not direct,
        #     not pinned,
        #     not backtrack_cause,
        #     inferred_depth,
        #     requested_order,
        #     not unfree,
        #     identifier,
        # )

    @override
    def find_matches(
        self,
        identifier: str,
        requirements: Mapping[str, Iterator[Requirement]],
        incompatibilities: Mapping[str, Iterator[Candidate]],
    ) -> Iterable[Candidate]:
        # constraint = _get_with_identifier(
        #     self._constraints,
        #     identifier,
        #     default=Constraint.empty(),
        # )
        return self._factory.find_candidates(
            identifier=identifier,
            requirements=requirements,
            # constraint=constraint,
            prefers_installed=False,
            incompatibilities=incompatibilities,
            is_satisfied_by=self.is_satisfied_by,
        )

    @override
    @lru_cache(maxsize=None)
    def is_satisfied_by(self, requirement: Requirement, candidate: Candidate) -> bool:
        return requirement.is_satisfied_by(candidate)

    @override
    def get_dependencies(self, candidate: Candidate) -> Sequence[Requirement]:
        with_requires = not self._ignore_dependencies
        return [r for r in candidate.iter_dependencies(with_requires) if r is not None]
