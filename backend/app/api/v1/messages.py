from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.message import Message, Bookmark
from app.services.ai_moderation import AIModerationService
from datetime import datetime
from typing import List

router = APIRouter()
ai_moderation = AIModerationService()

class MessageCreate(BaseModel):
    channel_id: str
    content: str
    parent_id: str | None = None
    mentions: List[str] = []
    attachments: List[dict] = []

class MessageResponse(BaseModel):
    id: str
    channel_id: str
    user_id: str
    content: str
    parent_id: str | None
    is_edited: bool
    is_pinned: bool
    reactions: dict
    mentions: List[str]
    attachments: List[dict]
    created_at: datetime
    updated_at: datetime

class MessageUpdate(BaseModel):
    content: str

class ReactionAdd(BaseModel):
    emoji: str

@router.post("/", response_model=MessageResponse, status_code=201)
async def create_message(
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # AI Moderation
    moderation_result = await ai_moderation.moderate_content(message_data.content)
    
    if moderation_result["is_toxic"]:
        raise HTTPException(status_code=400, detail="Message flagged by AI moderation")
    
    message = Message(
        channel_id=message_data.channel_id,
        user_id=current_user["id"],
        content=message_data.content,
        parent_id=message_data.parent_id,
        mentions=message_data.mentions,
        attachments=message_data.attachments,
        ai_moderation_score=max(moderation_result["scores"].values()) if moderation_result["scores"] else 0,
        ai_moderation_flags=[k for k, v in moderation_result["categories"].items() if v]
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    return MessageResponse(
        id=str(message.id),
        channel_id=str(message.channel_id),
        user_id=str(message.user_id),
        content=message.content,
        parent_id=str(message.parent_id) if message.parent_id else None,
        is_edited=message.is_edited,
        is_pinned=message.is_pinned,
        reactions=message.reactions,
        mentions=message.mentions,
        attachments=message.attachments,
        created_at=message.created_at,
        updated_at=message.updated_at
    )

@router.get("/{channel_id}", response_model=List[MessageResponse])
async def get_messages(
    channel_id: str,
    limit: int = Query(50, le=100),
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Message)
        .where(Message.channel_id == channel_id, Message.is_deleted == False)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    messages = result.scalars().all()
    
    return [
        MessageResponse(
            id=str(msg.id),
            channel_id=str(msg.channel_id),
            user_id=str(msg.user_id),
            content=msg.content,
            parent_id=str(msg.parent_id) if msg.parent_id else None,
            is_edited=msg.is_edited,
            is_pinned=msg.is_pinned,
            reactions=msg.reactions,
            mentions=msg.mentions,
            attachments=msg.attachments,
            created_at=msg.created_at,
            updated_at=msg.updated_at
        )
        for msg in messages
    ]

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_update: MessageUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if str(message.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    message.content = message_update.content
    message.is_edited = True
    await db.commit()
    await db.refresh(message)
    
    return MessageResponse(
        id=str(message.id),
        channel_id=str(message.channel_id),
        user_id=str(message.user_id),
        content=message.content,
        parent_id=str(message.parent_id) if message.parent_id else None,
        is_edited=message.is_edited,
        is_pinned=message.is_pinned,
        reactions=message.reactions,
        mentions=message.mentions,
        attachments=message.attachments,
        created_at=message.created_at,
        updated_at=message.updated_at
    )

@router.delete("/{message_id}")
async def delete_message(
    message_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if str(message.user_id) != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    message.is_deleted = True
    await db.commit()
    return {"message": "Message deleted"}

@router.post("/{message_id}/reactions")
async def add_reaction(
    message_id: str,
    reaction: ReactionAdd,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    reactions = message.reactions or {}
    if reaction.emoji not in reactions:
        reactions[reaction.emoji] = []
    if current_user["id"] not in reactions[reaction.emoji]:
        reactions[reaction.emoji].append(current_user["id"])
    
    message.reactions = reactions
    await db.commit()
    return {"message": "Reaction added"}

@router.post("/{message_id}/bookmark")
async def bookmark_message(
    message_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    bookmark = Bookmark(user_id=current_user["id"], message_id=message_id)
    db.add(bookmark)
    await db.commit()
    return {"message": "Message bookmarked"}
