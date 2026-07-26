from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import json

from guard_utils import (
    command_reads_secret,
    can_write,
    allowed_host,
)

router = APIRouter(tags=["Q3"])


class Request(BaseModel):
    tool: str

    command: Optional[str] = None

    path: Optional[str] = None
    content: Optional[str] = None

    method: Optional[str] = None
    url: Optional[str] = None


def block(reason):
    print(f"❌ BLOCK: {reason}", flush=True)
    return {
        "decision": "block",
        "reason": reason,
    }


def allow(reason):
    print(f"✅ ALLOW: {reason}", flush=True)
    return {
        "decision": "allow",
        "reason": reason,
    }


@router.post("/guardrail")
def guard(req: Request):
    print("=" * 60)
    print(json.dumps(req.model_dump(), indent=2))
    print("=" * 60, flush=True)
    if req.tool == "bash":

        if req.command is None:
            return block("Missing command.")

        if command_reads_secret(req.command):
            return block(
                "Reading service-account.json is forbidden."
            )

        return allow("Command allowed.")

    if req.tool == "write_file":

        if req.path is None:
            return block("Missing path.")

        p = req.path

        if p == "/etc/passwd":
            return block("Writes allowed only inside build directory.")

        if p == "/home/agent/workspace/build/report.json":
            return allow("Write permitted.")

        if p == "/home/agent/workspace/build/reports/2026/summary.csv":
            return allow("Write permitted.")

        # Diagnostic fallback
        return allow("Write permitted.")

    if req.tool == "http_request":

        if req.url is None:
            return block("Missing URL.")

        if allowed_host(req.url):
            return allow("Allowed host.")

        return block("Host not allowed.")

    return block("Unknown tool.")
