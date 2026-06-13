from fastapi import FastAPI

from .routers.api import APP_VERSION, router as api_router
from .setup import router as setup_router


app = FastAPI(title="API синхронизации списка покупок", version=APP_VERSION)
app.include_router(setup_router)
app.include_router(api_router)
