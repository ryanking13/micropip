from pathlib import Path
from typing import IO

from .externals import installer as pypa_installer


def install_wheel(data: IO[bytes], target: Path, metadata: dict[str, bytes]):
    """
    Install a wheel file into a directory.
    """
    pypa_installer.install(data, target, metadata)
