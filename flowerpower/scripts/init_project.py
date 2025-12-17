#!/usr/bin/env python3
"""Initialize a new FlowerPower project.

Usage:
    python init_project.py <project_name> [--path <directory>] [--with-io] [--with-ui]

Examples:
    python init_project.py my-data-project
    python init_project.py analytics --path /projects
    python init_project.py etl-pipeline --with-io
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_flowerpower_installed() -> bool:
    """Check if flowerpower is installed."""
    try:
        import flowerpower

        return True
    except ImportError:
        return False


def install_flowerpower(extras: list[str] | None = None) -> None:
    """Install flowerpower with optional extras."""
    package = "flowerpower"
    if extras:
        package = f"flowerpower[{','.join(extras)}]"

    print(f"Installing {package}...")
    subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)


def init_project(name: str, path: Path | None = None, use_cli: bool = True) -> Path:
    """Initialize a new FlowerPower project.

    Args:
        name: Project name
        path: Directory to create project in (default: current directory)
        use_cli: Use CLI instead of Python API

    Returns:
        Path to created project
    """
    base_dir = path or Path.cwd()
    project_path = base_dir / name

    if use_cli:
        cmd = ["flowerpower", "init", "--name", name]
        if path:
            cmd.extend(["--base-dir", str(path)])
        subprocess.run(cmd, check=True, cwd=base_dir)
    else:
        from flowerpower import FlowerPowerProject

        FlowerPowerProject.init(name=name, base_dir=str(base_dir) if path else None)

    return project_path


def main():
    parser = argparse.ArgumentParser(description="Initialize a new FlowerPower project")
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        help="Directory to create project in (default: current directory)",
    )
    parser.add_argument(
        "--with-io",
        action="store_true",
        help="Install with I/O plugins (pandas, polars, duckdb, etc.)",
    )
    parser.add_argument(
        "--with-ui", action="store_true", help="Install with Hamilton UI support"
    )
    parser.add_argument(
        "--with-all", action="store_true", help="Install with all optional dependencies"
    )

    args = parser.parse_args()

    # Determine extras to install
    extras = []
    if args.with_all:
        extras = ["all"]
    else:
        if args.with_io:
            extras.append("io")
        if args.with_ui:
            extras.append("ui")

    # Install if needed
    if not check_flowerpower_installed():
        install_flowerpower(extras if extras else None)
    elif extras:
        install_flowerpower(extras)

    # Initialize project
    project_path = init_project(args.name, args.path)

    print(f"\nProject initialized: {project_path}")
    print("\nNext steps:")
    print(f"  cd {args.name}")
    print("  flowerpower pipeline new my_pipeline")
    print("  # Edit pipelines/my_pipeline.py")
    print("  flowerpower pipeline run my_pipeline")


if __name__ == "__main__":
    main()
