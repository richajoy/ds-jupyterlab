# JupyterLab Multi-Environment: Local Python Development

A quickly updatable local environment for data science prototyping and Python development. Seamlessly navigate between multiple Python kernels while eliminating dependency conflicts through conda's isolation capabilities and UV's accelerated package management. Effortlessly switch between Python versions and benchmark installation performance across pip, conda, and UV package managers.

## Prerequisites

- Docker: Make sure you have Docker installed and running on your system
- Docker Desktop (recommended for easy container management)
- At least 4GB of available RAM for running containers
- Internet connection for downloading packages during benchmarking

## Key Features

- **Quick Local Development Environment**: Set up a complete data science environment in minutes without modifying your host system
- **Multiple Python Versions**: Test code across Python 3.10, 3.11, and 3.12 environments without version conflicts
- **Dependency Management**: Avoid dependency hell by isolating environments with specific package versions
- **Package Manager Benchmarking**: Compare installation performance between pip, conda, and uv
- **Dynamic Environment Configuration**: Easily add or modify environments through the `environments.yaml` file
- **Reproducible Setup**: Consistent environment setup across different machines

## Version 1 (v1) Features

### Environment Setup
- Base image: `continuumio/miniconda3`
- JupyterLab configuration with XSRF checks disabled for easier local development
- Four conda environments configured with different Python versions:
  - `ds-env-py312-ml`: Python 3.12 with ML packages
  - `ds-env-py312`: Standard Python 3.12 environment
  - `ds-env-py311`: Python 3.11 environment
  - `ds-env-py310`: Python 3.10 environment

### Dynamic Environment Configuration
- Simple YAML-based configuration for adding or modifying environments
- Add as many Python environments as needed without Docker expertise
- Specify exact package versions for complete reproducibility
- Mix conda and uv packages in the same environment for optimal performance
- Example configuration in `environments.yaml`:
```yaml
environments:
  - name: "ds-env-py312-ml"
    python: "3.12"
    conda_packages:
      - numpy=1.26
      - scipy=1.13
    uv_packages:
      - scikit-learn==1.5.0
      - pandas==2.2.3
```

### Package Management
- Three package managers available:
  - pip: Standard Python package manager
  - conda: Conda package manager for environment management
  - uv: Fast Python package installer and resolver

### Benchmarking
- Included `benchmark_package_managers.py` script for testing installation performance
- The benchmark script tests multiple packages across all three package managers
- Detailed performance metrics and comparisons provided

## Usage

### Building the Docker Image
```bash
docker build -t jupyter-uv-ds .
```

### Running the Container
```bash
docker run -p 8889:8888 -d --name jupyter-uv-ml jupyter-uv-ds
```

### Running Benchmarks
1. Access JupyterLab at http://localhost:8889
2. Create a new notebook with your desired kernel
3. Run the benchmark script using:
   ```python
   %run /home/jupyter/benchmark_package_managers.py
   ```
   Or copy the script contents into a notebook cell

## Environment Details

The environments are defined in `environments.yaml` and are set up by the `setup_envs.sh` script during image building.

### ds-env-py312-ml (ML Environment)
- Python 3.12
- Core packages via conda: numpy, scipy
- ML packages via uv: scikit-learn, pandas, seaborn, transformers, pillow, nltk, requests

### Other Environments
Each environment has specific versions of packages appropriate for that Python version.

## Future Development

For future versions, maintain backward compatibility with this v1 release. Use Docker tags for versioning:

```bash
# View available versions
docker images jupyter-uv-ds

# Run a specific version
docker run -p 8889:8888 -d jupyter-uv-ds:v1
```