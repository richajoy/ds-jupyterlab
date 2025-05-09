# Base image with Miniconda
FROM continuumio/miniconda3

# Set environment variables
ENV SHELL=/bin/bash \
    NB_USER=jupyter \
    NB_UID=1000 \
    NB_GID=100

# Create a new user
RUN groupadd -g ${NB_GID} ${NB_USER} || true && \
    useradd -m -s ${SHELL} -N -u ${NB_UID} -g ${NB_GID} ${NB_USER}

# Set working directory
WORKDIR /home/${NB_USER}

# Install JupyterHub, JupyterLab, and required tools
RUN conda install -y \
    jupyterhub \
    jupyterlab \
    notebook && \
    conda install -y -c conda-forge yq && \
    conda clean -afy

# Install uv package manager using pip with correct path setup
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir uv && \
    # Find the actual path to the uv executable
    UV_PATH=$(find /opt/conda -name "uv" -type f -executable | head -n 1) && \
    if [ -z "$UV_PATH" ]; then \
        echo "uv executable not found" && exit 1; \
    else \
        echo "Found uv at $UV_PATH" && \
        # Make it available in PATH
        mkdir -p /usr/local/bin && \
        ln -sf "$UV_PATH" /usr/local/bin/uv && \
        # Verify installation
        uv --version; \
    fi

# Make sure /usr/local/bin is in PATH for all environments
ENV PATH="/usr/local/bin:${PATH}"

# Copy environment definitions, setup script, and benchmark tool
COPY environments.yaml /home/${NB_USER}/environments.yaml
COPY setup_envs.sh /home/${NB_USER}/setup_envs.sh
COPY benchmark_package_managers.py /home/${NB_USER}/benchmark_package_managers.py

# Make script executable and run it to create environments
RUN chmod +x /home/${NB_USER}/setup_envs.sh && \
    /home/${NB_USER}/setup_envs.sh

# Create notebooks directory
RUN mkdir -p /home/${NB_USER}/notebooks
WORKDIR /home/${NB_USER}/notebooks

# Configure Jupyter to only show our custom kernels
RUN mkdir -p /etc/jupyter
RUN echo 'c = get_config()' > /etc/jupyter/jupyter_config.py && \
    echo 'c.KernelSpecManager.ensure_native_kernel = False' >> /etc/jupyter/jupyter_config.py && \
    echo "c.KernelSpecManager.whitelist = ['ds-env-py312-ml', 'ds-env-py312', 'ds-env-py311', 'ds-env-py310']" >> /etc/jupyter/jupyter_config.py

# Expose port
EXPOSE 8888

# Set entrypoint to start JupyterLab directly with CORS allowed
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", \
     "--ServerApp.token=''", "--ServerApp.password=''", "--ServerApp.disable_check_xsrf=True", \
     "--ServerApp.allow_origin='*'", "--ServerApp.allow_credentials=True"]
