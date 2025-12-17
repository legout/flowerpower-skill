# FlowerPower Configuration Reference

## project.yml

```yaml
# conf/project.yml
name: my-project

# Optional: Hamilton adapter configurations
adapter:
  hamilton_tracker:
    enabled: true
    api_url: "http://localhost:8000"
  mlflow:
    enabled: false
    tracking_uri: "mlruns/"
```

## Pipeline Configuration

```yaml
# conf/pipelines/<name>.yml

# Parameters accessible via PARAMS in Python
params:
  input_config:
    source_path: "data/input.csv"
    batch_size: 100
  processing:
    normalize: true
    fill_missing: "mean"
  output_config:
    destination: "data/output.parquet"

# Execution configuration
run:
  # Required: Output nodes from Hamilton DAG
  final_vars:
    - processed_data
    - summary_stats
  
  # Optional: Input values to DAG
  inputs:
    start_date: "2024-01-01"
    end_date: "2024-12-31"
  
  # Optional: Hamilton runtime config
  config:
    environment: "production"
  
  # Optional: Executor settings
  executor:
    type: threadpool          # synchronous | threadpool | processpool | ray | dask
    max_workers: 4            # For threadpool/processpool
    num_cpus: 8               # For ray/dask
  
  # Optional: Retry configuration
  retry:
    max_retries: 3
    retry_delay: 1.0          # Base delay in seconds
    jitter_factor: 0.1        # Random factor 0-1
    retry_exceptions:
      - requests.exceptions.HTTPError
      - ConnectionError
  
  # Optional: Logging
  log_level: INFO             # DEBUG | INFO | WARNING | ERROR | CRITICAL
  
  # Optional: Caching
  cache:
    recompute:
      - expensive_node        # Force recompute these nodes
  # Or disable: cache: false
  
  # Optional: Lifecycle callbacks
  on_success:
    function: "my_module.success_handler"
    args: ["arg1"]
    kwargs:
      key: "value"
  
  on_failure:
    function: "my_module.failure_handler"
  
  # Optional: Additional modules to compose
  additional_modules:
    - shared_setup
    - pipelines.utilities
  
  # Optional: Force reload modules
  reload: false

# Optional: Pipeline-specific adapter overrides
adapter:
  hamilton_tracker:
    enabled: true
```

## RunConfig (Python API)

```python
from flowerpower.cfg.pipeline.run import RunConfig
from flowerpower.cfg.pipeline.builder import RunConfigBuilder

# Direct instantiation
config = RunConfig(
    inputs={"key": "value"},
    final_vars=["output_node"],
    config={"env": "prod"},
    executor={"type": "threadpool", "max_workers": 4},
    retry={"max_retries": 3, "retry_delay": 1.0},
    log_level="INFO",
    cache={"recompute": ["node_a"]},
    additional_modules=["setup_module"],
    reload=False
)

# Using builder pattern
config = (
    RunConfigBuilder(pipeline_name='my_pipeline')
    .with_inputs({"key": "value"})
    .with_final_vars(["output"])
    .with_log_level("DEBUG")
    .with_retries(max_attempts=3, delay=1.0)
    .with_executor(type="threadpool", max_workers=8)
    .build()
)

# Run with config
result = project.run('my_pipeline', run_config=config)

# Override config with kwargs (kwargs take precedence)
result = project.run(
    'my_pipeline',
    run_config=config,
    log_level="DEBUG",  # Overrides config
    inputs={"key": "new_value"}  # Overrides config
)
```

## CLI RunConfig Options

```bash
# All options
flowerpower pipeline run my_pipeline \
  --inputs '{"key": "value"}' \
  --final-vars '["output"]' \
  --config '{"env": "prod"}' \
  --executor threadpool \
  --executor-max-workers 4 \
  --executor-num-cpus 8 \
  --max-retries 3 \
  --retry-delay 2.0 \
  --jitter-factor 0.2 \
  --log-level DEBUG \
  --cache '{"recompute": ["node"]}' \
  --base-dir /path/to/project

# Using RunConfig file
flowerpower pipeline run my_pipeline --run-config ./run_config.yaml

# Using RunConfig JSON string
flowerpower pipeline run my_pipeline --run-config '{"inputs": {"k": "v"}, "log_level": "INFO"}'

# Mix RunConfig with kwargs (kwargs override)
flowerpower pipeline run my_pipeline \
  --run-config ./run_config.yaml \
  --log-level DEBUG
```

## Executor Configurations

### Synchronous (Default)
```yaml
executor:
  type: synchronous
```

### Thread Pool
```yaml
executor:
  type: threadpool
  max_workers: 8
```

### Process Pool
```yaml
executor:
  type: processpool
  max_workers: 4
```

### Ray
```yaml
executor:
  type: ray
  num_cpus: 16
```

### Dask
```yaml
executor:
  type: dask
  num_cpus: 16
```

## Retry Configurations

```yaml
retry:
  max_retries: 5
  retry_delay: 2.0
  jitter_factor: 0.2
  retry_exceptions:
    - requests.exceptions.HTTPError
    - requests.exceptions.ConnectionError
    - TimeoutError
    - ConnectionResetError
```

The actual delay is calculated as:
```
delay = retry_delay * (1 + random.uniform(-jitter_factor, jitter_factor))
```
