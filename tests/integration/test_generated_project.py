"""Check that a renamed copy retains the Dagster runtime contract."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_renamed_project_loads_and_executes_smoke_without_secrets() -> None:
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory)
        package = destination / "src" / "example_dagster_app"
        shutil.copytree(ROOT / "src" / "template_python_dagster", package)
        for source in package.rglob("*.py"):
            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    "template_python_dagster", "example_dagster_app"
                ),
                encoding="utf-8",
            )
        code = """from dagster import Definitions
from example_dagster_app.dagster.definitions import defs
Definitions.validate_loadable(defs)
job = defs.resolve_job_def('runtime_smoke_job')
assert job.execute_in_process().success
assert job.required_resource_keys == {'io_manager'}
"""
        environment = {
            "PATH": os.environ["PATH"],
            "PYTHONPATH": str(destination / "src"),
        }
        result = subprocess.run(  # noqa: S603 - executes the current test interpreter
            [sys.executable, "-c", code],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
