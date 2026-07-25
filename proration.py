from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Q2"])


class ProrationRequest(BaseModel):
    old_price: float
    new_price: float
    days_remaining: float
    days_in_actual_month: float
    spec: str


@router.post("/proration")
def proration(req: ProrationRequest):

    if req.spec == "v1":
        divisor = 30.0

    elif req.spec == "v2":
        divisor = float(req.days_in_actual_month)

    else:
        return {"charge": 0}

    charge = (
        (req.new_price - req.old_price)
        * (req.days_remaining / divisor)
    )

    return {
        "charge": charge
    }