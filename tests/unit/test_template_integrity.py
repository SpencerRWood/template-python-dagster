import tomllib
from importlib import import_module
from pathlib import Path
from typing import Any

from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[2]


def load_pyproject() -> dict[str, Any]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_package_can_be_imported() -> None:
    package = import_module("template_python_dagster")

    assert package.__all__ == ()


def test_template_project_metadata_describes_scaffold() -> None:
    pyproject = load_pyproject()
    project = pyproject["project"]

    assert project["name"] == "template-python-dagster"
    assert project["description"].startswith("A typed Python template for Dagster")
    assert project["requires-python"] == ">=3.14"
    requirements = {
        Requirement(item).name: Requirement(item) for item in project["dependencies"]
    }
    assert {
        "dagster",
        "dagster-postgres",
        "sqlalchemy",
        "psycopg2-binary",
    } <= requirements.keys()
    assert "psycopg" not in requirements
    assert str(requirements["dagster"].specifier) == "==1.13.24"
    assert str(requirements["dagster-postgres"].specifier) == "==0.29.24"
    assert str(requirements["sqlalchemy"].specifier) == "==2.0.54"
    assert str(requirements["psycopg2-binary"].specifier) == "==2.9.13"
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    locked = {package["name"] for package in lock["package"]}
    assert "psycopg2-binary" in locked
    assert "psycopg" not in locked


def test_template_declares_typed_src_package() -> None:
    pyproject = load_pyproject()
    project = pyproject["project"]
    tool = pyproject["tool"]
    hatch_targets = tool["hatch"]["build"]["targets"]

    assert (ROOT / "src" / "template_python_dagster" / "py.typed").is_file()
    assert "Typing :: Typed" in project["classifiers"]
    assert hatch_targets["wheel"]["packages"] == [
        "src/template_python_dagster",
    ]
    assert tool["coverage"]["run"]["source"] == ["template_python_dagster"]


def test_docker_entrypoint_targets_definitions_module() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "template_python_dagster.dagster.definitions" in dockerfile
    assert "dagster api grpc" in dockerfile


def test_centralized_release_contract() -> None:
    workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "SpencerRWood/workflows/.github/workflows/release.yml@v1" in workflow
    assert (
        "SpencerRWood/workflows/.github/workflows/container-release.yml@v1" in workflow
    )
    release_config = tomllib.loads(
        (ROOT / ".github/release.toml").read_text(encoding="utf-8")
    )
    assert release_config["build"]["python_package"] is True
    assert release_config["release"]["semantic_release"] is True
    assert "dagster" not in release_config
