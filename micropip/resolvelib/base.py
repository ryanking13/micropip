"""copied and modified from pip/.../resolvelib/base.py"""
from collections.abc import Iterable

# from pip._internal.models.link import Link, links_equivalent
# from pip._internal.req.req_install import InstallRequirement
# from pip._internal.utils.hashes import Hashes
from .._vendored.packaging.src.packaging.utils import NormalizedName
from .._vendored.packaging.src.packaging.version import Version

# CandidateLookup = tuple["Candidate" | None, InstallRequirement | None]


def format_name(project: NormalizedName, extras: frozenset[NormalizedName]) -> str:
    if not extras:
        return project
    extras_expr = ",".join(sorted(extras))
    return f"{project}[{extras_expr}]"


class Requirement:
    @property
    def project_name(self) -> NormalizedName:
        """The "project name" of a requirement.

        This is different from ``name`` if this requirement contains extras,
        in which case ``name`` would contain the ``[...]`` part, while this
        refers to the name of the project.
        """
        raise NotImplementedError("Subclass should override")

    @property
    def name(self) -> str:
        """The name identifying this requirement in the resolver.

        This is different from ``project_name`` if this requirement contains
        extras, where ``project_name`` would not contain the ``[...]`` part.
        """
        raise NotImplementedError("Subclass should override")

    def is_satisfied_by(self, candidate: "Candidate") -> bool:
        return False

    # def get_candidate_lookup(self) -> CandidateLookup:
    #     raise NotImplementedError("Subclass should override")

    def format_for_error(self) -> str:
        raise NotImplementedError("Subclass should override")


class Candidate:
    @property
    def project_name(self) -> NormalizedName:
        """The "project name" of the candidate.

        This is different from ``name`` if this candidate contains extras,
        in which case ``name`` would contain the ``[...]`` part, while this
        refers to the name of the project.
        """
        raise NotImplementedError("Override in subclass")

    @property
    def name(self) -> str:
        """The name identifying this candidate in the resolver.

        This is different from ``project_name`` if this candidate contains
        extras, where ``project_name`` would not contain the ``[...]`` part.
        """
        raise NotImplementedError("Override in subclass")

    @property
    def version(self) -> Version:
        raise NotImplementedError("Override in subclass")

    @property
    def is_installed(self) -> bool:
        raise NotImplementedError("Override in subclass")

    @property
    def is_editable(self) -> bool:
        raise NotImplementedError("Override in subclass")

    @property
    # def source_link(self) -> Link | None:
    #     raise NotImplementedError("Override in subclass")

    def iter_dependencies(self, with_requires: bool) -> Iterable[Requirement | None]:
        raise NotImplementedError("Override in subclass")

    # def get_install_requirement(self) -> InstallRequirement | None:
    #     raise NotImplementedError("Override in subclass")

    def format_for_error(self) -> str:
        raise NotImplementedError("Subclass should override")
