# Hamilton Function Patterns for FlowerPower

## Basic Function Pattern

Each function becomes a node in the DAG. Parameters are dependencies.

```python
def raw_data() -> dict:
    """Entry point - no dependencies."""
    return {"values": [1, 2, 3]}

def processed_data(raw_data: dict) -> dict:
    """Depends on raw_data node."""
    return {"values": [v * 2 for v in raw_data["values"]]}

def final_result(processed_data: dict) -> str:
    """Depends on processed_data node."""
    return str(processed_data)
```

## Loading Pipeline Parameters

```python
from pathlib import Path
from flowerpower.cfg import Config

# Load parameters from conf/pipelines/<name>.yml
PARAMS = Config.load(
    Path(__file__).parents[1], 
    pipeline_name="my_pipeline"
).pipeline.h_params
```

## @parameterize Decorator

Inject configuration parameters into functions.

```python
from hamilton.function_modifiers import parameterize

# Config: params.greeting: {message: "Hello"}
@parameterize(**PARAMS.greeting)
def greeting(message: str) -> str:
    return message

# Config: params.target: {name: "World"}
@parameterize(**PARAMS.target)
def target(name: str) -> str:
    return name

# Multiple parameter sets create multiple nodes
# Config: params.data_sources: {source_a: {path: "a.csv"}, source_b: {path: "b.csv"}}
@parameterize(**PARAMS.data_sources)
def load_source(path: str) -> pd.DataFrame:
    return pd.read_csv(path)
```

## @config.when Decorator

Conditional node execution based on runtime config.

```python
from hamilton.function_modifiers import config

@config.when(environment="production")
def database_connection__prod() -> Connection:
    return ProductionDB.connect()

@config.when(environment="development")
def database_connection__dev() -> Connection:
    return LocalDB.connect()

# Hamilton selects based on config={"environment": "production"}
```

## @tag Decorator

Attach metadata to nodes for filtering/grouping.

```python
from hamilton.function_modifiers import tag

@tag(stage="ingestion", priority="high")
def ingest_data() -> pd.DataFrame:
    return pd.read_csv("data.csv")

@tag(stage="transform", priority="medium")
def transform_data(ingest_data: pd.DataFrame) -> pd.DataFrame:
    return ingest_data.dropna()

@tag(stage="output", priority="high")
def save_output(transform_data: pd.DataFrame) -> str:
    transform_data.to_parquet("output.parquet")
    return "saved"
```

## @extract_columns Decorator

Extract DataFrame columns as separate nodes.

```python
from hamilton.function_modifiers import extract_columns
import pandas as pd

@extract_columns("name", "age", "salary")
def user_data() -> pd.DataFrame:
    return pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [30, 25],
        "salary": [50000, 45000]
    })

# Creates nodes: name, age, salary (each as pd.Series)
def average_age(age: pd.Series) -> float:
    return age.mean()
```

## @check_output Decorator

Validate function outputs.

```python
from hamilton.function_modifiers import check_output
import pandera as pa

schema = pa.DataFrameSchema({
    "id": pa.Column(int, checks=pa.Check.gt(0)),
    "value": pa.Column(float, nullable=False)
})

@check_output(schema=schema)
def validated_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    return raw_data
```

## @does Decorator

Apply transformation to function output.

```python
from hamilton.function_modifiers import does
import pandas as pd

def _to_uppercase(df: pd.DataFrame) -> pd.DataFrame:
    return df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)

@does(_to_uppercase)
def normalized_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    return raw_data
```

## Helper Functions

Functions starting with `_` are not included in DAG.

```python
def _validate_input(data: dict) -> bool:
    """Helper function - not a node."""
    return "required_key" in data

def processed_data(raw_data: dict) -> dict:
    """This is a node."""
    if not _validate_input(raw_data):
        raise ValueError("Invalid input")
    return raw_data
```

## Complete Pipeline Example

```python
# pipelines/etl_pipeline.py
from pathlib import Path
from hamilton.function_modifiers import parameterize, tag, extract_columns
import pandas as pd

from flowerpower.cfg import Config

PARAMS = Config.load(
    Path(__file__).parents[1], 
    pipeline_name="etl_pipeline"
).pipeline.h_params

# --- Ingestion ---

@tag(stage="ingestion")
@parameterize(**PARAMS.source)
def raw_data(file_path: str) -> pd.DataFrame:
    """Load raw data from source."""
    return pd.read_csv(file_path)

# --- Transformation ---

@tag(stage="transform")
def cleaned_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate data."""
    return raw_data.dropna().drop_duplicates()

@tag(stage="transform")
@extract_columns("revenue", "quantity", "date")
def sales_metrics(cleaned_data: pd.DataFrame) -> pd.DataFrame:
    """Extract sales metrics."""
    return cleaned_data[["revenue", "quantity", "date"]]

@tag(stage="transform")
def daily_totals(revenue: pd.Series, quantity: pd.Series, date: pd.Series) -> pd.DataFrame:
    """Aggregate daily totals."""
    df = pd.DataFrame({"revenue": revenue, "quantity": quantity, "date": date})
    return df.groupby("date").sum().reset_index()

# --- Output ---

@tag(stage="output")
@parameterize(**PARAMS.output)
def save_results(daily_totals: pd.DataFrame, output_path: str) -> str:
    """Save results to parquet."""
    daily_totals.to_parquet(output_path)
    return f"Saved to {output_path}"

@tag(stage="output")
def summary(daily_totals: pd.DataFrame, save_results: str) -> dict:
    """Generate summary statistics."""
    return {
        "total_revenue": daily_totals["revenue"].sum(),
        "total_quantity": daily_totals["quantity"].sum(),
        "num_days": len(daily_totals),
        "output_file": save_results
    }
```

Corresponding config:

```yaml
# conf/pipelines/etl_pipeline.yml
params:
  source:
    file_path: "data/sales.csv"
  output:
    output_path: "output/daily_totals.parquet"

run:
  final_vars:
    - summary
  executor:
    type: threadpool
    max_workers: 4
```
