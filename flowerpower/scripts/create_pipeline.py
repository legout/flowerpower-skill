#!/usr/bin/env python3
"""Create a new FlowerPower pipeline.

Usage:
    python create_pipeline.py <pipeline_name> [--path <project_dir>] [--overwrite]

Examples:
    python create_pipeline.py data_ingestion
    python create_pipeline.py etl_process --path /projects/my-project
    python create_pipeline.py analytics --overwrite
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime


PIPELINE_TEMPLATE = '''# FlowerPower pipeline {name}
# Created on {date}

from pathlib import Path
from hamilton.function_modifiers import parameterize

from flowerpower.cfg import Config

# Load pipeline parameters from conf/pipelines/{name}.yml
PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="{name}"
).pipeline.h_params


# Helper functions (prefix with underscore - not included in DAG)
def _validate_data(data: dict) -> bool:
    """Validate input data."""
    return data is not None and len(data) > 0


# Pipeline functions (each becomes a node in the DAG)

@parameterize(**PARAMS.get("input_config", {{"source": "default"}}))
def load_data(source: str) -> dict:
    """Load data from source.
    
    Args:
        source: Data source identifier
        
    Returns:
        Loaded data dictionary
    """
    # TODO: Implement data loading logic
    return {{"source": source, "data": []}}


def validate_data(load_data: dict) -> dict:
    """Validate loaded data.
    
    Args:
        load_data: Data from load_data node
        
    Returns:
        Validated data
    """
    if not _validate_data(load_data):
        raise ValueError("Invalid data")
    return load_data


def process_data(validate_data: dict) -> dict:
    """Process validated data.
    
    Args:
        validate_data: Data from validate_data node
        
    Returns:
        Processed data
    """
    # TODO: Implement processing logic
    return {{"processed": True, **validate_data}}


def final_output(process_data: dict) -> str:
    """Generate final output.
    
    Args:
        process_data: Data from process_data node
        
    Returns:
        Output summary string
    """
    return f"Processed {{len(process_data)}} items"
'''


CONFIG_TEMPLATE = """# Pipeline configuration for {name}
# See references/configuration.md for all options

params:
  input_config:
    source: "data/input.csv"

run:
  final_vars:
    - final_output
  
  # Executor configuration
  executor:
    type: synchronous
    # type: threadpool
    # max_workers: 4
  
  # Retry configuration
  # retry:
  #   max_retries: 3
  #   retry_delay: 1.0
  #   jitter_factor: 0.1
  
  # Logging level
  log_level: INFO
"""


def create_pipeline(
    name: str,
    project_path: Path | None = None,
    overwrite: bool = False,
    use_cli: bool = True,
) -> tuple[Path, Path]:
    """Create a new pipeline.

    Args:
        name: Pipeline name
        project_path: Path to FlowerPower project
        overwrite: Overwrite existing pipeline
        use_cli: Use CLI instead of Python API

    Returns:
        Tuple of (module_path, config_path)
    """
    base_dir = project_path or Path.cwd()

    if use_cli:
        cmd = ["flowerpower", "pipeline", "new", name]
        if overwrite:
            cmd.append("--overwrite")
        subprocess.run(cmd, check=True, cwd=base_dir)

        module_path = base_dir / "pipelines" / f"{name}.py"
        config_path = base_dir / "conf" / "pipelines" / f"{name}.yml"
    else:
        from flowerpower import FlowerPowerProject

        project = FlowerPowerProject.load(str(base_dir))
        project.pipeline_manager.new(name=name, overwrite=overwrite)

        module_path = base_dir / "pipelines" / f"{name}.py"
        config_path = base_dir / "conf" / "pipelines" / f"{name}.yml"

    return module_path, config_path


def create_pipeline_from_template(
    name: str, project_path: Path | None = None, overwrite: bool = False
) -> tuple[Path, Path]:
    """Create pipeline using templates (no CLI dependency).

    Args:
        name: Pipeline name
        project_path: Path to FlowerPower project
        overwrite: Overwrite existing pipeline

    Returns:
        Tuple of (module_path, config_path)
    """
    base_dir = project_path or Path.cwd()

    pipelines_dir = base_dir / "pipelines"
    config_dir = base_dir / "conf" / "pipelines"

    module_path = pipelines_dir / f"{name}.py"
    config_path = config_dir / f"{name}.yml"

    # Check existing
    if not overwrite:
        if module_path.exists():
            raise FileExistsError(f"Pipeline module already exists: {module_path}")
        if config_path.exists():
            raise FileExistsError(f"Pipeline config already exists: {config_path}")

    # Create directories
    pipelines_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)

    # Write files
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    module_content = PIPELINE_TEMPLATE.format(name=name, date=date_str)
    config_content = CONFIG_TEMPLATE.format(name=name)

    module_path.write_text(module_content)
    config_path.write_text(config_content)

    return module_path, config_path


def main():
    parser = argparse.ArgumentParser(description="Create a new FlowerPower pipeline")
    parser.add_argument(
        "name", help="Pipeline name (use underscores, e.g., my_pipeline)"
    )
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Path to FlowerPower project (default: current directory)",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing pipeline"
    )
    parser.add_argument(
        "--template-only",
        action="store_true",
        help="Use templates instead of CLI (no flowerpower installation required)",
    )

    args = parser.parse_args()

    # Validate name
    if "-" in args.name:
        print(f"Warning: Pipeline names should use underscores, not hyphens")
        args.name = args.name.replace("-", "_")
        print(f"Using: {args.name}")

    try:
        if args.template_only:
            module_path, config_path = create_pipeline_from_template(
                args.name, args.path, args.overwrite
            )
        else:
            module_path, config_path = create_pipeline(
                args.name, args.path, args.overwrite
            )

        print(f"\nPipeline created:")
        print(f"  Module: {module_path}")
        print(f"  Config: {config_path}")
        print("\nNext steps:")
        print(f"  1. Edit {module_path} to implement pipeline logic")
        print(f"  2. Configure parameters in {config_path}")
        print(f"  3. Run: flowerpower pipeline run {args.name}")

    except FileExistsError as e:
        print(f"Error: {e}")
        print("Use --overwrite to replace existing pipeline")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error creating pipeline: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
