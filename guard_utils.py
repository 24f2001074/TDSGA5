from pathlib import Path
from urllib.parse import urlparse
import os
import base64

WORKSPACE = "/home/agent/workspace"
BUILD_DIR = "/home/agent/workspace/build"
SECRET = "/home/agent/service-account.json"

SECRET_B64 = base64.b64encode(SECRET.encode()).decode()

ALLOWED_HOSTS = {
    "api.github.com",
    "objects.githubusercontent.com",
}


def normalize_path(path: str) -> str:
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)

    if not os.path.isabs(path):
        path = os.path.join(WORKSPACE, path)

    return os.path.abspath(os.path.normpath(path))


def is_secret(path: str) -> bool:
    return normalize_path(path) == SECRET


def command_reads_secret(command: str) -> bool:
    cmd = os.path.expandvars(command)
    cmd = os.path.expanduser(cmd)

    # Direct secret path
    if SECRET in cmd:
        return True

    # Base64 encoded secret path
    if SECRET_B64 in cmd:
        return True

    return False


def can_write(path: str) -> bool:
    target = normalize_path(path)

    return (
        target == BUILD_DIR
        or target.startswith(BUILD_DIR + "/")
    )


def allowed_host(url: str) -> bool:
    try:
        host = urlparse(url).hostname

        if not host:
            return False

        host = host.lower().rstrip(".")

        return host in ALLOWED_HOSTS

    except Exception:
        return False