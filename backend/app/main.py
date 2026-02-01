from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import settings
from app.api.v1 import auth, channels, messages, users, files, analytics
from app.websocket.manager import ConnectionManager
from app.core.database import engine, Base
from app.services.rabbitmq import RabbitMQService

manager = ConnectionManager()
rabbitmq_service = RabbitMQService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create uploads directory
    uploads_dir = Path("/app/uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    await rabbitmq_service.connect()
    yield
    # Shutdown
    await rabbitmq_service.close()

app = FastAPI(
    title="Chat API with AI Moderation",
    version="1.0.0",
    description="Real-time chat application with AI-powered content moderation",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving files
uploads_dir = Path("/app/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# API Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(channels.router, prefix="/api/v1/channels", tags=["channels"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["messages"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.handle_message(user_id, data)
    except WebSocketDisconnect:
        await manager.disconnect(user_id)

@app.get("/")
async def root():
    return {
        "message": "Chat API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
