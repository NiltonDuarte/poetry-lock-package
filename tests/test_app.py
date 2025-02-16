import os
from typing import Callable

import toml

from poetry_lock_package.app import (
    clean_dependencies,
    collect_dependencies,
    lock_package_name,
    project_root_dependencies,
    run,
)
from poetry_lock_package.util import read_toml


def always(result: bool) -> Callable[[str], bool]:
    def impl(_: str) -> bool:
        return result

    return impl


def test_main():
    run(
        should_create_tests=False,
        run_poetry_build_wheel=False,
        move_package_after_build=False,
        clean_up_project=True,
        allow_package_filter=lambda _: True,
        add_root=True,
        ignore_editable_dependencies=False,
    )
    assert not os.path.exists(
        "poetry-lock-package-lock"
    ), "Should have been removed by clean"


def test_lock_package_name():
    assert lock_package_name("a") == "a-lock"
    assert lock_package_name("a-b") == "a-b-lock"
    assert lock_package_name("a_b") == "a_b_lock"


def test_collect_dependencies():
    with open("tests/resources/example1.lock", "r") as lock_file:
        lock_toml = toml.load(lock_file)
        assert clean_dependencies(
            collect_dependencies(lock_toml, ["atomicwrites"], always(True), False)
        ) == {
            "atomicwrites": {
                "python": ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
                "version": "1.4.0",
            }
        }

        assert clean_dependencies(
            collect_dependencies(lock_toml, ["loguru"], always(True), False)
        )["win32-setctime"] == {
            "markers": 'sys_platform == "win32"',
            "python": ">=3.5",
            "version": "1.0.3",
        }


def test_collect_dependencies_ignore_editable():
    with open("tests/resources/editable_dependency.lock", "r") as lock_file:
        lock_toml = toml.load(lock_file)
    assert (
        clean_dependencies(
            collect_dependencies(lock_toml, ["my_editable_package"], always(True), True)
        )
        == {}
    )

    assert clean_dependencies(
        collect_dependencies(
            lock_toml, ["my_editable_package", "atomicwrites"], always(True), True
        )
    ) == {
        "atomicwrites": {
            "python": ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
            "version": "1.4.0",
        }
    }


def test_pybluez_git_reference():
    lock_toml = read_toml("tests/resources/pybluez_git.lock")
    project_toml = read_toml("tests/resources/pybluez_git.toml")
    root_dependencies = project_root_dependencies(project_toml)

    assert clean_dependencies(
        collect_dependencies(lock_toml, root_dependencies, always(True), False)
    ) == {
        "PyBluez": {
            "python": ">=3.5",
            "version": "0.30",
        }
    }


def test_project_root_dependencies() -> None:
    project = read_toml("pyproject.toml")

    root_deps = project_root_dependencies(project)

    assert root_deps, "Should find root dependencies"
    assert "python" not in root_deps, "Should ignore python"
