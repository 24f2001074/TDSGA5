from fastapi import FastAPI

app = FastAPI(
    title="TDS GA5 API",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "running",
        "message": "TDS GA5 API is live!"
    }