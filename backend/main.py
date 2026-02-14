"""
ShellGuard Backend - FastAPI Entry Point
"""
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from api.websocket_handler import WebSocketHandler
from api.routes import router as api_router
from data.database import init_database
from archestra.observability import setup_observability

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    await init_database()
    setup_observability()
    print("🛡️ ShellGuard Backend Started")
    yield
    # Shutdown
    print("🛡️ ShellGuard Backend Stopped")

app = FastAPI(
    title="ShellGuard API",
    description="AI Terminal Copilot with Safety Rails",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(api_router, prefix="/api")

# WebSocket endpoint for terminal
@app.websocket("/ws/terminal")
async def terminal_websocket(websocket: WebSocket):
    """WebSocket endpoint for terminal sessions"""
    handler = WebSocketHandler(websocket)
    await handler.handle()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "development"
    )
