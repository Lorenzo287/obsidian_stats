import os
from pathlib import Path

# To use this: 
# 1. Create a file named '.env' in this directory.
# 2. Add your paths there (see .env.example)

def load_env(file_path=".env"):
    """Simple parser to load environment variables from a .env file."""
    if not os.path.exists(file_path):
        return
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
            except ValueError:
                continue

# Load local .env if it exists
load_env()

# Paths (using environment variables; error if critical ones are missing)
vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
if not vault_path:
    # If not set, we default to current directory but warn/handle in scripts
    # Alternatively, you can raise an error if it's mandatory
    OBSIDIAN_VAULT_PATH = Path("journal_placeholder") 
else:
    OBSIDIAN_VAULT_PATH = Path(vault_path)

DATA_OUTPUT_CSV = os.getenv("DATA_OUTPUT_CSV", "data_output.csv")
PROD_OUTPUT_CSV = os.getenv("PROD_OUTPUT_CSV", "prod_output.csv")
