from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserStatus
from app.models.message import Message
from app.models.channel import Channel
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()

class AnalyticsDashboard(BaseModel):
    active_users: int
    total_messages: int
    total_channels: int
    messages_today: int
    online_users: int
    ai_moderation_flags: int

@router.get("/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Active users (logged in last 24h)
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.last_seen >= yesterday)
    )
    active_users = active_users_result.scalar()
    
    # Total messages
    total_messages_result = await db.execute(
        select(func.count(Message.id)).where(Message.is_deleted == False)
    )
    total_messages = total_messages_result.scalar()
    
    # Total channels
    total_channels_result = await db.execute(
        select(func.count(Channel.id)).where(Channel.is_active == True)
    )
    total_channels = total_channels_result.scalar()
    
    # Messages today
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    messages_today_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.created_at >= today,
            Message.is_deleted == False
        )
    )
    messages_today = messages_today_result.scalar()
    
    # Online users
    online_users_result = await db.execute(
        select(func.count(User.id)).where(User.status == UserStatus.ONLINE)
    )
    online_users = online_users_result.scalar()
    
    # AI moderation flags - count messages with non-empty flags array
    try:
        ai_flags_result = await db.execute(
            select(func.count(Message.id)).where(
                Message.ai_moderation_flags != []
            )
        )
        ai_moderation_flags = ai_flags_result.scalar() or 0
    except Exception as e:
        print(f"AI flags query error: {e}")
        ai_moderation_flags = 0
    
    return AnalyticsDashboard(
        active_users=active_users,
        total_messages=total_messages,
        total_channels=total_channels,
        messages_today=messages_today,
        online_users=online_users,
        ai_moderation_flags=ai_moderation_flags
    )
