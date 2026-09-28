"""Asset jobs for this code location."""

from dagster import define_asset_job, in_process_executor, job, mem_io_manager, op

example_job = define_asset_job("example_job", selection="example_message")


@op
def runtime_smoke() -> str:
    """Prove the shared Dagster runtime can execute and log a run."""
    return "ok"


@job(executor_def=in_process_executor, resource_defs={"io_manager": mem_io_manager})
def runtime_smoke_job() -> None:
    """Infrastructure validation only; independent of application resources."""
    runtime_smoke()
