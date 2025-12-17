#!/usr/bin/env python3
"""List available FlowerPower pipelines.

Usage:
    python list_pipelines.py [--path <project_dir>] [--format <format>]

Examples:
    python list_pipelines.py
    python list_pipelines.py --path /projects/my-project
    python list_pipelines.py --format json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def list_pipelines_cli(
    base_dir: Path | None = None, output_format: str = "table"
) -> None:
    """List pipelines using CLI.

    Args:
        base_dir: Project directory
        output_format: Output format (table, json, yaml)
    """
    cmd = ["flowerpower", "pipeline", "show-pipelines"]

    if base_dir:
        cmd.extend(["--base-dir", str(base_dir)])

    cmd.extend(["--format", output_format])

    subprocess.run(cmd, check=True)


def list_pipelines_api(base_dir: Path | None = None) -> list[str]:
    """List pipelines using Python API.

    Args:
        base_dir: Project directory

    Returns:
        List of pipeline names
    """
    from flowerpower import FlowerPowerProject

    project = FlowerPowerProject.load(str(base_dir) if base_dir else ".")
    return project.pipeline_manager.list()


def list_pipelines_filesystem(base_dir: Path | None = None) -> list[dict]:
    """List pipelines by scanning filesystem (no flowerpower required).

    Args:
        base_dir: Project directory

    Returns:
        List of pipeline info dicts
    """
    project_dir = base_dir or Path.cwd()
    pipelines_dir = project_dir / "pipelines"
    config_dir = project_dir / "conf" / "pipelines"

    if not pipelines_dir.exists():
        return []

    pipelines = []

    for module_file in pipelines_dir.glob("*.py"):
        if module_file.name.startswith("_"):
            continue

        name = module_file.stem
        config_file = config_dir / f"{name}.yml"

        pipelines.append(
            {
                "name": name,
                "module": str(module_file),
                "config": str(config_file) if config_file.exists() else None,
                "has_config": config_file.exists(),
            }
        )

    return sorted(pipelines, key=lambda p: p["name"])


def main():
    parser = argparse.ArgumentParser(description="List available FlowerPower pipelines")
    parser.add_argument("--path", "-p", type=Path, help="Path to FlowerPower project")
    parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json", "yaml", "simple"],
        default="table",
        help="Output format",
    )
    parser.add_argument(
        "--use-api", action="store_true", help="Use Python API instead of CLI"
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan filesystem (no flowerpower installation required)",
    )

    args = parser.parse_args()

    try:
        if args.scan:
            pipelines = list_pipelines_filesystem(args.path)

            if args.format == "json":
                print(json.dumps(pipelines, indent=2))
            elif args.format == "simple":
                for p in pipelines:
                    print(p["name"])
            else:
                print(f"\nPipelines in {args.path or Path.cwd()}:")
                print("-" * 50)
                for p in pipelines:
                    status = "OK" if p["has_config"] else "MISSING CONFIG"
                    print(f"  {p['name']:30} [{status}]")
                print(f"\nTotal: {len(pipelines)} pipeline(s)")

        elif args.use_api:
            pipelines = list_pipelines_api(args.path)

            if args.format == "json":
                print(json.dumps(pipelines, indent=2))
            elif args.format == "simple":
                for name in pipelines:
                    print(name)
            else:
                print(f"\nAvailable pipelines:")
                print("-" * 30)
                for name in pipelines:
                    print(f"  {name}")
                print(f"\nTotal: {len(pipelines)} pipeline(s)")
        else:
            list_pipelines_cli(args.path, args.format)

    except subprocess.CalledProcessError as e:
        print(f"Error listing pipelines: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
