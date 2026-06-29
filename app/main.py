from fastapi import FastAPI
from app.core.config import settings
from contextlib import asynccontextmanager
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.chats.router import router as chats_router
from app.modules.messages.router import router as messages_router
from app.modules.websocket.router import router as websocket_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.models import *
from app.common.request_exeption_handler import register_exeption_handler
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('App Starting')
    yield
    logger.info('App Stopping')

app = FastAPI(
    title = settings.APP_NAME,
    version = '1.0.0',
    lifespan = lifespan
)

register_exeption_handler(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins = settings.ALLOW_ORIGINS.split(','),
    allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_credentials = True,
    allow_headers = ['*']
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(websocket_router)

@app.get('/')
def root():
    return {
        'message': 'Chat App Is Runing'
    }

@app.get('/health')
def health():
    return {
        'status': 'healthy'
    }