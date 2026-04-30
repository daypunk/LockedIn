"""Project-wide defaults.

The vault path resolution order:
    1. --vault CLI flag
    2. SELFGRAPH_VAULT environment variable
    3. ~/.selfgraph/
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VAULT_DIR = Path.home() / ".selfgraph"
DEFAULT_OUTPUTS_DIRNAME = "outputs"
DEFAULT_TEMPLATE = "career"
ENV_VAULT = "SELFGRAPH_VAULT"
ENV_ALLOW_API_KEY = "SELFGRAPH_ALLOW_API_KEY"


def resolve_vault(cli_value: str | None = None) -> Path:
    if cli_value:
        return Path(cli_value).expanduser()
    env_value = os.environ.get(ENV_VAULT)
    if env_value:
        return Path(env_value).expanduser()
    return DEFAULT_VAULT_DIR
