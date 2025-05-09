#!/usr/bin/env bash
set -euo pipefail

# Ensure yq (https://github.com/mikefarah/yq) is available
# uv must be available on PATH from its Rust installer

ENV_FILE="/home/jupyter/environments.yaml"
COUNT=$(yq '.environments | length' "$ENV_FILE")

for i in $(seq 0 $((COUNT - 1))); do
  NAME=$(yq ".environments[$i].name"    "$ENV_FILE")
  # Remove any quotes from environment name
  NAME=$(echo $NAME | tr -d '"')
  PY_VER=$(yq ".environments[$i].python" "$ENV_FILE")
  # Join conda packages with spaces
  CONDA_PKGS=$(yq ".environments[$i].conda_packages[]" "$ENV_FILE" | xargs)
  UV_PKGS=$(yq ".environments[$i].uv_packages[]"       "$ENV_FILE" | xargs)

  # Remove any quotes from Python version
  PY_VER=$(echo $PY_VER | tr -d '"')
  echo "👉 Creating Conda env '$NAME' with Python $PY_VER"
  conda create -y -n "$NAME" python=$PY_VER $CONDA_PKGS -c conda-forge 

  echo "👉 Activating '$NAME' and installing ipykernel and pure‑Python packages via uv"
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "$NAME"
  # First make sure ipykernel is installed for kernel registration
  conda install -y ipykernel
  # Then install the UV packages
  uv pip install $UV_PKGS                                     

  echo "👉 Registering Jupyter kernel for '$NAME'"
  python -m ipykernel install \
      --user \
      --name "$NAME" \
      --display-name "$NAME (Py$PY_VER)"                   

  conda deactivate
done