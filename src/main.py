import logging

from fastapi import FastAPI
import uvicorn

from routes import app_router
from utils.env_load_util import EnvLoadUtil

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
    uvicorn.run("main:app", host=EnvLoadUtil.load_env("APPLICATION_SERVER_HOST"), port=int(EnvLoadUtil.load_env("APPLICATION_SERVER_PORT")), reload=True)
