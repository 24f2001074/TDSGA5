from pathlib import Path
from urllib.parse import urlparse
import os
import base64
import re

WORKSPACE = Path("/home/agent/workspace")
BUILD_DIR = (WORKSPACE / "build").resolve()
SECRET = Path("/home/agent/service-account.json").resolve()

SECRET_B64 = base64.b64encode(str(SECRET).encode()).decode()

ALLOWED_HOSTS = {
    "api.github.com",
    "objects.githubusercontent.com",
}


def normalize_path(path: str) -> Path:
    # Expand common shell shortcuts manually
    path = path.replace("$HOME", "/home/agent")
    path = path.replace("~", "/home/agent")

    path = os.path.expandvars(path)

    if not os.path.isabs(path):
        path = str(WORKSPACE / path)

    return Path(path).resolve(strict=False)


def is_secret(path: str) -> bool:
    return normalize_path(path) == SECRET


def command_reads_secret(command: str) -> bool:
    print("=" * 50)
    print("RAW COMMAND :", command)

    # Detect the exact base64 string
    if SECRET_B64 in command:
        print("MATCH: BASE64")
        return True

    # Expand shell shortcuts
    cmd = command.replace("$HOME", "/home/agent")
    cmd = cmd.replace("~", "/home/agent")
    cmd = os.path.expandvars(cmd)

    print("NORMALIZED :", cmd)

    # Direct secret path
    if str(SECRET) in cmd:
        print("MATCH: DIRECT PATH")
        return True

    # Relative traversal
    if re.search(r"\.\./+service-account\.json\b", cmd):
        print("MATCH: RELATIVE")
        return True

    return False


def can_write(path: str) -> bool:
    target = normalize_path(path)

    print("=" * 50)
    print("WRITE INPUT :", path)
    print("WRITE TARGET:", target)

    try:
        target.relative_to(BUILD_DIR)
        return True
    except ValueError:
        return False


def allowed_host(url: str) -> bool:
    try:
        host = urlparse(url).hostname

        if not host:
            return False

        host = host.lower().rstrip(".")

        return host in ALLOWED_HOSTS

    except Exception:
        return False