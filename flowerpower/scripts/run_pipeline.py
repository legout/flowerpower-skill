#!/usr/bin/env python3
"""Run a FlowerPower pipeline.

Usage:
    python run_pipeline.py <pipeline_name> [options]

Examples:
    python run_pipeline.py my_pipeline
    python run_pipeline.py etl --inputs '{"key": "value"}'
    python run_pipeline.py analytics --executor threadpool --max-workers 4
    python run_pipeline.py data_process --final-vars '["output_a", "output_b"]'
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_pipeline_cli(
    name: str,
    base_dir: Path | None = None,
    inputs: dict | None = None,
    final_vars: list[str] | None = None,
    executor: str | None = None,
    max_workers: int | None = None,
    max_retries: int | None = None,
    retry_delay: float | None = None,
    log_level: str | None = None,
    run_config: str | None = None,
) -> None:
    """Run pipeline using CLI.

    Args:
        name: Pipeline name
        base_dir: Project directory
        inputs: Input parameters
        final_vars: Output variables
        executor: Executor type
        max_workers: Max workers for thread/process pool
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries
        log_level: Logging level
        run_config: Path to RunConfig file or JSON string
    """
    cmd = ["flowerpower", "pipeline", "run", name]

    if base_dir:
        cmd.extend(["--base-dir", str(base_dir)])

    if inputs:
        cmd.extend(["--inputs", json.dumps(inputs)])

    if final_vars:
        cmd.extend(["--final-vars", json.dumps(final_vars)])

    if executor:
        cmd.extend(["--executor", executor])

    if max_workers:
        cmd.extend(["--executor-max-workers", str(max_workers)])

    if max_retries is not None:
        cmd.extend(["--max-retries", str(max_retries)])

    if retry_delay is not None:
        cmd.extend(["--retry-delay", str(retry_delay)])

    if log_level:
        cmd.extend(["--log-level", log_level])

    if run_config:
        cmd.extend(["--run-config", run_config])

    subprocess.run(cmd, check=True)


def run_pipeline_api(
    name: str,
    base_dir: Path | None = None,
    inputs: dict | None = None,
    final_vars: list[str] | None = None,
    executor: str | None = None,
    max_workers: int | None = None,
    max_retries: int | None = None,
    retry_delay: float | None = None,
    log_level: str | None = None,
) -> dict:
    """Run pipeline using Python API.

    Args:
        name: Pipeline name
        base_dir: Project directory
        inputs: Input parameters
        final_vars: Output variables
        executor: Executor type
        max_workers: Max workers for thread/process pool
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries
        log_level: Logging level

    Returns:
        Pipeline results
    """
    from flowerpower import FlowerPowerProject

    project = FlowerPowerProject.load(str(base_dir) if base_dir else ".")

    # Build kwargs
    kwargs = {}

    if inputs:
        kwargs["inputs"] = inputs

    if final_vars:
        kwargs["final_vars"] = final_vars

    if executor:
        executor_config = {"type": executor}
        if max_workers:
            executor_config["max_workers"] = max_workers
        kwargs["executor"] = executor_config

    if max_retries is not None or retry_delay is not None:
        retry_config = {}
        if max_retries is not None:
            retry_config["max_retries"] = max_retries
        if retry_delay is not None:
            retry_config["retry_delay"] = retry_delay
        kwargs["retry"] = retry_config

    if log_level:
        kwargs["log_level"] = log_level

    return project.run(name, **kwargs)


def main():
    parser = argparse.ArgumentParser(description="Run a FlowerPower pipeline")
    parser.add_argument("name", help="Pipeline name")
    parser.add_argument("--path", "-p", type=Path, help="Path to FlowerPower project")
    parser.add_argument("--inputs", "-i", help="Input parameters as JSON string")
    parser.add_argument("--final-vars", "-o", help="Output variables as JSON list")
    parser.add_argument(
        "--executor",
        "-e",
        choices=["synchronous", "threadpool", "processpool", "ray", "dask"],
        help="Executor type",
    )
    parser.add_argument(
        "--max-workers", "-w", type=int, help="Max workers for threadpool/processpool"
    )
    parser.add_argument("--max-retries", type=int, help="Maximum retry attempts")
    parser.add_argument(
        "--retry-delay", type=float, help="Delay between retries in seconds"
    )
    parser.add_argument(
        "--log-level",
        "-l",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level",
    )
    parser.add_argument(
        "--run-config", help="Path to RunConfig YAML file or JSON string"
    )
    parser.add_argument(
        "--use-api", action="store_true", help="Use Python API instead of CLI"
    )

    args = parser.parse_args()

    # Parse JSON arguments
    inputs = json.loads(args.inputs) if args.inputs else None
    final_vars = json.loads(args.final_vars) if args.final_vars else None

    try:
        if args.use_api:
            result = run_pipeline_api(
                args.name,
                base_dir=args.path,
                inputs=inputs,
                final_vars=final_vars,
                executor=args.executor,
                max_workers=args.max_workers,
                max_retries=args.max_retries,
                retry_delay=args.retry_delay,
                log_level=args.log_level,
            )
            print("\nPipeline completed!")
            print(f"Results: {result}")
        else:
            run_pipeline_cli(
                args.name,
                base_dir=args.path,
                inputs=inputs,
                final_vars=final_vars,
                executor=args.executor,
                max_workers=args.max_workers,
                max_retries=args.max_retries,
                retry_delay=args.retry_delay,
                log_level=args.log_level,
                run_config=args.run_config,
            )

    except subprocess.CalledProcessError as e:
        print(f"Error running pipeline: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
