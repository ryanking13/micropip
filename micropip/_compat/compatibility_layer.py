from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..wheelinfo import PackageData


class CompatibilityLayer(ABC):
    """
    CompatibilityLayer represents the interface that must be implemented for each viable environment.

    All of the following methods / properties must be implemented for use both inside and outside of pyodide.
    """

    class HttpStatusError(ABC, Exception):
        status_code: int
        message: str

        @abstractmethod
        def __init__(self, status_code: int, message: str):
            pass

    class loadedPackages(ABC):
        @staticmethod
        @abstractmethod
        def to_py():
            pass

    @staticmethod
    @abstractmethod
    def repodata_info() -> dict[str, str]:
        pass

    @staticmethod
    @abstractmethod
    def repodata_packages() -> dict[str, dict[str, Any]]:
        pass

    @staticmethod
    @abstractmethod
    async def fetch_bytes(url: str, kwargs: dict[str, str]) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    async def fetch_string_and_headers(
        url: str, kwargs: dict[str, Any]
    ) -> tuple[str, dict[str, str]]:
        pass

    @staticmethod
    @abstractmethod
    async def install(
        data: bytes,
        filename: str,
        install_dir: str,
        installer: str,
        source: str,
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    async def loadPackage(names: str | list[str]) -> None:
        pass

    @staticmethod
    @abstractmethod
    def to_js(
        obj: Any,
        /,
        *,
        depth: int = -1,
        pyproxies: Any,
        create_pyproxies: bool = True,
        dict_converter: Any,
        default_converter: Any,
    ) -> Any:
        pass
