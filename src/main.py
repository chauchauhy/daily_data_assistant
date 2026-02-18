import logging

from fastapi import FastAPI
import uvicorn

from routes import app_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ],
)

app = FastAPI()
app.include_router(app_router, prefix="/router", tags=["kmb_router"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
