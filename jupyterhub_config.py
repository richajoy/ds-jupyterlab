c = get_config()

# Spawn with JupyterHub single-user server
c.Spawner.cmd = ['jupyterhub-singleuser']

# Set timeouts to allow sufficient startup time
c.Spawner.start_timeout = 60
c.Spawner.http_timeout = 60

# Set the default URL to JupyterLab
c.Spawner.default_url = '/lab'

# Create a default user with admin privileges and no password
c.JupyterHub.authenticator_class = 'dummy'
c.DummyAuthenticator.password = ""

# Create a default admin user for easier testing
c.Authenticator.admin_users = {'admin'}

# Create a static API token for accessing JupyterHub
# This allows direct access without needing login forms
c.JupyterHub.api_tokens = {
    'jupyter-token': 'admin',  # Map token to the admin user
}

# Allow named servers
c.JupyterHub.allow_named_servers = True
