import importlib
import importlib.metadata
import shutil
import site
import sys
from pathlib import Path
from textwrap import dedent

from .._mock_package import _add_in_memory_distribution, _remove_in_memory_distribution

MOCK_INSTALL_NAME_MEMORY = "micropip in-memory mock package"
MOCK_INSTALL_NAME_PERSISTENT = "micropip mock package"


def add_mock_package(
    name: str,
    version: str,
    *,
    modules: dict[str, str | None] | None = None,
    persistent: bool = False,
) -> None:
    """
    Add a mock version of a package to the package dictionary.

    This means that if it is a dependency, it is skipped on install.

    By default a single empty module is installed with the same
    name as the package. You can alternatively give one or more modules to make a
    set of named modules.

    The modules parameter is usually a dictionary mapping module name to module text.

    .. code-block:: python

        {
            "mylovely_module":'''
            def module_method(an_argument):
                print("This becomes a module level argument")

            module_value = "this value becomes a module level variable"
            print("This is run on import of module")
            '''
        }

    If you are adding the module in non-persistent mode, you can also pass functions
    which are used to initialize the module on loading (as in `importlib.abc.loader.exec_module` ).
    This allows you to do things like use `unittest.mock.MagicMock` classes for modules.

    .. code-block:: python

        def init_fn(module):
            module.dict["WOO"]="hello"
            print("Initing the module now!")

        ...

        {
            "mylovely_module": init_fn
        }

    Parameters
    ----------
    name :

        Package name to add

    version :

        Version of the package. This should be a semantic version string,
        e.g. 1.2.3

    modules :

        Dictionary of module_name:string pairs.
        The string contains the source of the mock module or is blank for
        an empty module.

    persistent :

        If this is True, modules will be written to the file system, so they
        persist between runs of python (assuming the file system persists).
        If it is False, modules will be stored inside micropip in memory only.
    """
    if modules is None:
        # make a single mock module with this name
        modules = {name: ""}
    # make the metadata
    METADATA = f"""Metadata-Version: 1.1
Name: {name}
Version: {version}
Summary: {name} mock package generated by micropip
Author-email: {name}@micro.pip.non-working-fake-host
"""
    for n in modules.keys():
        METADATA += f"Provides:{n}\n"

    if persistent:
        # make empty mock modules with the requested names in user site packages
        site_packages = Path(site.getusersitepackages())
        # in pyodide site packages isn't on sys.path initially
        if not site_packages.exists():
            site_packages.mkdir(parents=True, exist_ok=True)
        if site_packages not in sys.path:
            sys.path.append(str(site_packages))
        metadata_dir = site_packages / (name + "-" + version + ".dist-info")
        metadata_dir.mkdir(parents=True, exist_ok=False)
        metadata_file = metadata_dir / "METADATA"
        record_file = metadata_dir / "RECORD"
        installer_file = metadata_dir / "INSTALLER"
        file_list = []
        file_list.append(metadata_file)
        file_list.append(installer_file)
        with open(metadata_file, "w") as mf:
            mf.write(METADATA)
        for n, s in modules.items():
            if s is None:
                s = ""
            s = dedent(s)
            path_parts = n.split(".")
            dir_path = Path(site_packages, *path_parts)
            dir_path.mkdir(exist_ok=True, parents=True)
            init_file = dir_path / "__init__.py"
            file_list.append(init_file)
            with open(init_file, "w") as f:
                f.write(s)
        with open(installer_file, "w") as f:
            f.write(MOCK_INSTALL_NAME_PERSISTENT)
        with open(record_file, "w") as f:
            for file in file_list:
                f.write(f"{str(file)},,{file.stat().st_size}\n")
            f.write(f"{str(record_file)},,\n")
    else:
        # make memory mocks of files
        INSTALLER = MOCK_INSTALL_NAME_MEMORY
        metafiles = {"METADATA": METADATA, "INSTALLER": INSTALLER}
        _add_in_memory_distribution(name, metafiles, modules)
    importlib.invalidate_caches()


def list_mock_packages() -> list[str]:
    packages = []
    for dist in importlib.metadata.distributions():
        installer = dist.read_text("INSTALLER")
        if installer is not None and (
            installer == MOCK_INSTALL_NAME_PERSISTENT
            or installer == MOCK_INSTALL_NAME_MEMORY
        ):
            packages.append(dist.name)
    return packages


def remove_mock_package(name: str) -> None:
    d = importlib.metadata.distribution(name)
    installer = d.read_text("INSTALLER")
    if installer == MOCK_INSTALL_NAME_MEMORY:
        _remove_in_memory_distribution(name)
        return
    elif installer is None or installer != MOCK_INSTALL_NAME_PERSISTENT:
        raise ValueError(
            f"Package {name} doesn't seem to be a micropip mock. \n"
            "Are you sure it was installed with micropip?"
        )
    # a real mock package - kill it
    # remove all files
    folders: set[Path] = set()
    if d.files is not None:
        for file in d.files:
            p = Path(file.locate())
            p.unlink()
            folders.add(p.parent)
    # delete all folders except site_packages
    # (that check is just to avoid killing
    # undesirable things in case of weird micropip errors)
    site_packages = Path(site.getusersitepackages())
    for f in folders:
        if f != site_packages:
            shutil.rmtree(f)
