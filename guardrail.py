from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

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
    return {
        "decision": "block",
        "reason": reason,
    }


def allow(reason):
    return {
        "decision": "allow",
        "reason": reason,
    }


@router.post("/guardrail")
def guard(req: Request):

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

        if can_write(req.path):
            return allow("Write permitted.")

        return block(
            "Writes allowed only inside build directory."
        )

    if req.tool == "http_request":

        if req.url is None:
            return block("Missing URL.")

        if allowed_host(req.url):
            return allow("Allowed host.")

        return block("Host not allowed.")

    return block("Unknown tool.")
