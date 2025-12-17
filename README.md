# FlowerPower Skill

🌸 A comprehensive skill for creating and managing data pipelines using the **FlowerPower** framework with **Hamilton DAGs** and **uv** package manager.

## Overview

This skill provides complete workflow support for the [FlowerPower](https://github.com/legout/flowerpower) data pipeline framework, enabling you to:

- Initialize new FlowerPower projects with proper structure
- Create pipelines using Hamilton functions and decorators
- Configure pipelines with YAML files
- Execute pipelines with multiple executor types
- Manage pipeline lifecycle operations

## 🚀 Quick Start

### Installation Methods

#### For Claude Code

**Option 1: Claude Marketplace (Recommended)**

Run this in Claude Code:
```bash
# Add marketplace
/plugin marketplace add legout/flowerpower-skill

# Install skill
/plugin install flowerpower@flowerpower-skill
```

**Option 2: OpenSkills**

Install OpenSkills first (if not already installed)

See: [Openskills Quick Start](https://github.com/numman-ali/openskills?tab=readme-ov-file#quick-start)
```bash

# Install skill using OpenSkills
openskills install legout/flowerpower

# Verify installation
openskills list
```

**Option 3: Manual Installation**

Clone repository
```bash

git clone https://github.com/legout/flowerpower-skill.git
```

Copy skill content to Claude skills directory
```bash
cp -r flowerpower-skill/flowerpower ~/.claude/skills/
# OR for project-specific installation
cp -r flowerpower-skill/flowerpower .claude/skills/
```

#### For OpenCode

**Option 1: OpenSkills (Recommended for OpenCode)**

Install OpenSkills first (if not already installed)

See: [Openskills Quick Start](https://github.com/numman-ali/openskills?tab=readme-ov-file#quick-start)

```bash

# Install skill using OpenSkills
openskills install legout/flowerpower

# Verify installation
openskills list
```

**Option 2: Manual Installation**
```bash
# Clone the repository
git clone https://github.com/legout/flowerpower-skill.git

# Copy skill content to OpenCode skills directory
cp -r flowerpower-skill/flowerpower ~/.openskills/skills/

# Verify installation
ls ~/.openskills/skills/flowerpower
```

### First Use

Once installed, simply ask Claude or OpenCode to work with FlowerPower:

```
Create a new flowerpower project called "data-analytics"
```

Or:

```
Help me create a pipeline that processes CSV files using flowerpower
```

The skill will automatically trigger and provide step-by-step guidance.

## 🛠️ What the Skill Provides

### 1. **Project Initialization**
- Creates standard FlowerPower directory structure
- Generates configuration files
- Supports optional dependencies (io, ui, all)

### 2. **Pipeline Creation**
- Hamilton function templates with proper decorators
- YAML configuration patterns
- Best practices for DAG design

### 3. **Execution Management**
- Multiple executor types (synchronous, threadpool, processpool, ray, dask)
- Retry configuration
- Logging and monitoring
- Both CLI and Python API support

### 4. **Configuration Reference**
- Complete YAML configuration patterns
- Hamilton function decorator examples
- Executor and retry configuration guides

## 📁 Project Structure

When you create a FlowerPower project with this skill, you get:

```
my-project/
├── conf/
│   ├── project.yml           # Global project settings
│   └── pipelines/
│       ├── pipeline_a.yml    # Pipeline configurations
│       └── pipeline_b.yml
├── pipelines/
│   ├── pipeline_a.py         # Hamilton functions
│   └── pipeline_b.py
└── hooks/                    # Optional lifecycle hooks
```

## 🎯 Usage Examples

### Creating a New Project

```
Initialize a flowerpower project called "etl-pipeline" with IO plugins
```

This will:
- Create the project structure
- Install flowerpower with `[io]` extras
- Generate initial configuration

### Creating a Pipeline

```
Create a pipeline called "data_processing" that loads CSV files and calculates statistics
```

This will:
- Create `pipelines/data_processing.py` with Hamilton functions
- Generate `conf/pipelines/data_processing.yml` configuration
- Provide examples for CSV loading and statistics calculation

### Running Pipelines

```
Run the data_processing pipeline with threadpool executor and 4 workers
```

This will execute:
```bash
flowerpower pipeline run data_processing --executor threadpool --executor-max-workers 4
```

## 📚 Available Resources

The skill includes comprehensive documentation:

### Core Files
- **`SKILL.md`** - Main skill instructions and quick reference
- **`references/overview.md`** - Key concepts and architecture
- **`references/configuration.md`** - Complete YAML configuration guide
- **`references/hamilton-patterns.md`** - Hamilton function patterns

### Scripts
- **`scripts/init_project.py`** - Initialize new projects
- **`scripts/create_pipeline.py`** - Create pipelines with templates
- **`scripts/run_pipeline.py`** - Execute pipelines with options
- **`scripts/list_pipelines.py`** - List available pipelines

## 🔧 Dependencies

### Required
- Python 3.8+
- `uv` package manager (recommended)
- `flowerpower` package

### Optional Dependencies
```bash
# I/O plugins (pandas, polars, duckdb, etc.)
uv pip install flowerpower[io]

# Hamilton UI
uv pip install flowerpower[ui]

# All optional dependencies
uv pip install flowerpower[all]
```

## 🎨 Examples

### Basic ETL Pipeline

```python
# pipelines/etl_pipeline.py
from hamilton.function_modifiers import parameterize, tag
import pandas as pd

PARAMS = Config.load(Path(__file__).parents[1], "etl_pipeline").pipeline.h_params

@tag(stage="extract")
@parameterize(**PARAMS.source)
def extract_data(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

@tag(stage="transform")
def transform_data(extract_data: pd.DataFrame) -> pd.DataFrame:
    return extract_data.dropna().drop_duplicates()

@tag(stage="load")
@parameterize(**PARAMS.output)
def load_data(transform_data: pd.DataFrame, output_path: str) -> str:
    transform_data.to_parquet(output_path)
    return f"Saved to {output_path}"
```

### Configuration

```yaml
# conf/pipelines/etl_pipeline.yml
params:
  source:
    file_path: "data/input.csv"
  output:
    output_path: "output/processed.parquet"

run:
  final_vars:
    - load_data
  executor:
    type: threadpool
    max_workers: 4
  retry:
    max_retries: 3
    retry_delay: 1.0
  log_level: INFO
```

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Test the skill with different scenarios
5. Submit a pull request

## 📖 Learn More

- [FlowerPower Documentation](https://legout.github.io/flowerpower/)
- [Hamilton Framework](https://github.com/apache/hamilton)
- [uv Package Manager](https://github.com/astral-sh/uv)
- [OpenSkills](https://github.com/numman-ali/openskills)

## 📄 License

This skill is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the FlowerPower community**