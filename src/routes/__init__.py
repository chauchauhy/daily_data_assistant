from fastapi import APIRouter
from routes.kmb_router import router as kmb_router
from routes.hko_router import router as hko_router


app_router = APIRouter()
app_router.include_router(kmb_router, tags=["kmb_router"])
app_router.include_router(hko_router, tags=["hko_router"])