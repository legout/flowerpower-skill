# FlowerPower Overview

## Key Concepts

### FlowerPower
Python framework for building, configuring, and executing data processing pipelines. Uses Hamilton for defining dataflows as DAGs.

### Hamilton DAG
Directed Acyclic Graph where each Python function is a node. Dependencies resolved by matching function parameter names to other function names.

### Pipeline
Executable unit of work defined as a Hamilton DAG. Each pipeline has:
- Python module (`pipelines/<name>.py`) - Hamilton functions
- YAML config (`conf/pipelines/<name>.yml`) - Parameters and run settings

### FlowerPowerProject
Primary entry point for programmatic interaction. Provides unified interface over PipelineManager.

### PipelineManager
Central orchestrator for pipeline operations: creation, execution, listing, visualization, deletion.

## Project Structure

```
my-project/
├── conf/
│   ├── project.yml           # Global project settings
│   └── pipelines/
│       ├── pipeline_a.yml    # Pipeline-specific config
│       └── pipeline_b.yml
├── pipelines/
│   ├── pipeline_a.py         # Hamilton functions
│   └── pipeline_b.py
├── hooks/                    # Optional lifecycle hooks
└── README.md
```

## Configuration Hierarchy

1. **project.yml** - Global settings, adapter configs
2. **pipelines/*.yml** - Pipeline params, run config, executor, retry
3. **RunConfig (runtime)** - Override via CLI or Python API

## Execution Flow

1. Load project configuration
2. Resolve pipeline module and config
3. Build Hamilton DAG from functions
4. Execute with configured executor
5. Return final_vars results
6. Invoke success/failure callbacks

## Executor Types

| Type | Description | Use Case |
|------|-------------|----------|
| `synchronous` | Sequential, single-process | Default, debugging |
| `threadpool` | Concurrent threads | I/O-bound (network, files) |
| `processpool` | Parallel processes | CPU-bound (computation) |
| `ray` | Distributed Ray cluster | Large-scale distributed |
| `dask` | Distributed Dask cluster | Large-scale distributed |

## Module Composition

Compose DAGs from multiple modules using `additional_modules`:

```python
result = project.run(
    'main_pipeline',
    additional_modules=['shared_setup', 'utilities'],
    final_vars=['output']
)
```

Resolution order:
1. Import string as-is
2. Replace hyphens with underscores
3. Import from `pipelines` package

Last module in list has highest precedence for conflicting node names.

## Async Execution

```python
import asyncio
from flowerpower.pipeline import PipelineManager

pm = PipelineManager(base_dir='.')

async def run_async():
    result = await pm.run_async('my_pipeline', final_vars=['output'])
    return result

asyncio.run(run_async())
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `FP_CONFIG_DIR` | Override `conf` directory name |
| `FP_PIPELINES_DIR` | Override `pipelines` directory name |
| `FP_HOOKS_DIR` | Override `hooks` directory name |
| `FP_CACHE_DIR` | Specify cache directory |

## Optional Dependencies

```bash
uv pip install flowerpower[io]      # I/O plugins (pandas, polars, duckdb, etc.)
uv pip install flowerpower[ui]      # Hamilton UI
uv pip install flowerpower[all]     # All optional dependencies
uv pip install flowerpower[io-legacy]  # Legacy Polars support
```

## I/O Plugins (flowerpower-io)

Supported formats and backends:
- **Files**: CSV, JSON, Parquet
- **Data Warehouses**: DeltaTable, DuckDB, PostgreSQL, MySQL, MSSQL, Oracle, SQLite
- **Messaging**: MQTT
- **DataFrames**: Pandas, Polars
