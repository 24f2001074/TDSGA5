from fastapi import FastAPI
from proration import router as proration_router

app = FastAPI(
    title="TDS GA5 API",
    version="1.0.0"
)

app.include_router(proration_router)
from guardrail import router as guard_router

app.include_router(guard_router)

@app.get("/")
def root():
    return {
        "status": "running"
    }
