from collections.abc import Iterable
from typing import override
from .._vendored.packaging.src.packaging.utils import NormalizedName, canonicalize_name
from .._vendored.packaging.src.packaging.version import Version
from .._vendored.packaging.src.packaging.requirements import Requirement

class BaseCandidate:
    """Adapted from pip/.../resolvelib/base.py"""

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
    def dependencies(self):
        raise NotImplementedError("Override in subclass")

    # @property
    # def is_installed(self) -> bool:
    #     raise NotImplementedError("Override in subclass")

    # @property
    # def is_editable(self) -> bool:
    #     raise NotImplementedError("Override in subclass")

    # @property
    # def source_link(self) -> Link | None:
    #     raise NotImplementedError("Override in subclass")

    # def iter_dependencies(self, with_requires: bool) -> Iterable[Requirement | None]:
    #     raise NotImplementedError("Override in subclass")

    # def get_install_requirement(self) -> [InstallRequirement]:
    #     raise NotImplementedError("Override in subclass")

    # def format_for_error(self) -> str:
    #     raise NotImplementedError("Subclass should override")

class PyPICandidate(BaseCandidate):
    """Candidate for a package from PyPI (or possibly another compatible index)"""
    def __init__(
        self,
        name: str,
        version: str,
        url: str | None = None,
        extras: set[str] | None = None,
    ):
        self._name = canonicalize_name(name)
        self._version = Version(version)
        self.url = url
        self.extras = extras

        # self._download()

        self._metadata = None
        self._dependencies = None

    def __repr__(self):
        if not self.extras:
            return f"<{self.name}=={self.version}>"
        return f"<{self.name}[{','.join(self.extras)}]=={self.version}>"

    @override
    @property
    def name(self):
        return self._name

    @override
    @property
    def project_name(self):
        return self._name

    @override
    @property
    def version(self):
        return self._version

    # async def _download(self):
    #     """
    #     Download a wheel.

    #     Parameters
    #     ----------
    #     wheel
    #         The wheel to add.

    #     extras
    #         Markers for optional dependencies.
    #         For example, `micropip.install("pkg[test]")`
    #         will pass `{"test"}` as the extras argument.

    #     specifier
    #         Requirement specifier, used only for logging.
    #         For example, `micropip.install("pkg>=1.0.0,!=2.0.0")`
    #         will pass `>=1.0.0,!=2.0.0` as the specifier argument.
    #     """
    #     normalized_name = canonicalize_name(wheel.name)
    #     self.locked[self.name] = PackageMetadata(
    #         name=wheel.name,
    #         version=str(wheel.version),
    #     )

    #     wheel_download_task = asyncio.create_task(wheel.download(self.fetch_kwargs))
    #     if self.deps:
    #         # Case 1) If metadata file is available,
    #         #         we can gather requirements without waiting for the wheel to be downloaded.
    #         if wheel.pep658_metadata_available():
    #             try:
    #                 await wheel.download_pep658_metadata(self.fetch_kwargs)
    #             except OSError:
    #                 # If something goes wrong while downloading the metadata,
    #                 # we have to wait for the wheel to be downloaded.
    #                 await wheel_download_task

    #             await asyncio.gather(
    #                 self.gather_requirements(wheel.requires(extras)),
    #                 wheel_download_task,
    #             )

    #         # Case 2) If metadata file is not available,
    #         #         we have to wait for the wheel to be downloaded.
    #         else:
    #             await wheel_download_task
    #             await self.gather_requirements(wheel.requires(extras))
    #     else:
    #         await wheel_download_task

    #     self.wheels.append(wheel)

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata_for_wheel(self.url)
        return self._metadata

    # @property
    # def requires_python(self):
    #     return self.metadata.get("Requires-Python")

    def _get_dependencies(self):
        deps = self.metadata.get_all("Requires-Dist", [])
        extras = self.extras if self.extras else [""]

        for d in deps:
            r = Requirement(d)
            if r.marker is None:
                yield r
            else:
                for e in extras:
                    if r.marker.evaluate({"extra": e}):
                        yield r

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._dependencies = list(self._get_dependencies())
        return self._dependencies


class LockFileCandidate(BaseCandidate):
    """Candidate for a package from a Pyodide lockfile"""
    def __init__(
        self,
        name: str,
        metadata: dict,  # metadata comes from the lockfile
    ):
        # Pyodide lockfile does not support extras
        self._metadata = metadata
        self._name = canonicalize_name(name)
        self._version = Version(metadata["version"])
        self._dependencies = metadata.get("depends", [])

    def __repr__(self):
        return f"<{self._name}=={self._version}>"

    @override
    @property
    def name(self):
        return self._name

    @override
    @property
    def project_name(self):
        return self._name

    @override
    @property
    def version(self):
        return self._version

    @override
    @property
    def dependencies(self):
        return self._dependencies
