from pathlib import Path
from urllib.parse import urlparse
import os
import re
import shlex

WORKSPACE = Path("/home/agent/workspace").resolve()
BUILD_DIR = (WORKSPACE / "build").resolve()

SECRET_FILE = Path("/home/agent/service-account.json").resolve()

ALLOWED_HOSTS = {
    "api.github.com",
    "objects.githubusercontent.com",
}


def normalize_path(path: str) -> Path:
    """
    Expand ~, $HOME and resolve relative paths
    relative to /home/agent/workspace.
    """

    path = os.path.expandvars(path)
    path = os.path.expanduser(path)

    p = Path(path)

    if not p.is_absolute():
        p = WORKSPACE / p

    return p.resolve()


def is_secret(path: str) -> bool:
    try:
        return normalize_path(path) == SECRET_FILE
    except Exception:
        return False


def can_write(path: str) -> bool:
    try:
        target = normalize_path(path)

        target.relative_to(BUILD_DIR)
        return True

    except Exception:
        return False


def allowed_host(url: str) -> bool:
    try:
        host = urlparse(url).hostname

        if host is None:
            return False

        host = host.lower().rstrip(".")

        return host in ALLOWED_HOSTS

    except Exception:
        return False


def extract_paths(command: str):
    """
    Very small shell parser.
    Returns filesystem-looking arguments.
    """

    try:
        tokens = shlex.split(command)
    except Exception:
        tokens = command.split()

    paths = []

    for token in tokens:
        if (
            "/" in token
            or token.startswith("~")
            or token.startswith("$HOME")
        ):
            paths.append(token)

    return paths
