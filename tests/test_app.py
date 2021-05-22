import os
from typing import Callable

import toml

from poetry_lock_package.lib import (
    clean_dependencies,
    collect_dependencies,
    lock_package_name,
    project_root_dependencies,
    run,
)
from poetry_lock_package.util import read_toml
from cleo.io.buffered_io import BufferedIO


def always(result: bool) -> Callable[[str], bool]:
    def impl(_: str) -> bool:
        return result

    return impl


def test_main():

    run(
        BufferedIO(),
        allow_package_filter=always(True),
        add_root=True,
    )
    assert not os.path.exists(
        "poetry-lock-package-lock"
    ), "Should have been removed by clean"


def test_lock_package_name():
    assert lock_package_name("a") == "a-lock"
    assert lock_package_name("a-b") == "a-b-lock"
    assert lock_package_name("a_b") == "a_b_lock"


def test_collect_dependencies():
    io = BufferedIO()
    with open("tests/resources/example1.lock", "r") as lock_file:
        lock_toml = toml.load(lock_file)
        assert clean_dependencies(
            collect_dependencies(io, lock_toml, ["atomicwrites"], always(True))
        ) == {
            "atomicwrites": {
                "python": ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
                "version": "1.4.0",
            }
        }

        assert clean_dependencies(
            collect_dependencies(io, lock_toml, ["loguru"], always(True))
        )["win32-setctime"] == {
            "markers": 'sys_platform == "win32"',
            "python": ">=3.5",
            "version": "1.0.3",
        }


def test_project_root_dependencies() -> None:
    project = read_toml("pyproject.toml")

    root_deps = project_root_dependencies(project)

    assert root_deps, "Should find root dependencies"
    assert "python" not in root_deps, "Should ignore python"
