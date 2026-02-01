from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.channel import Channel, ChannelType, MemberRole, channel_members
from datetime import datetime
from typing import List

router = APIRouter()

class ChannelCreate(BaseModel):
    name: str
    description: str | None = None
    type: ChannelType = ChannelType.PUBLIC

class ChannelResponse(BaseModel):
    id: str
    name: str
    description: str | None
    type: ChannelType
    owner_id: str
    created_at: datetime

class ChannelMemberAdd(BaseModel):
    user_id: str
    role: MemberRole = MemberRole.MEMBER

@router.post("/", response_model=ChannelResponse, status_code=201)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    channel = Channel(
        name=channel_data.name,
        description=channel_data.description,
        type=channel_data.type,
        owner_id=current_user["id"]
    )
    db.add(channel)
    await db.commit()
    await db.refresh(channel)
    
    # Add creator as owner
    await db.execute(
        insert(channel_members).values(
            channel_id=channel.id,
            user_id=current_user["id"],
            role=MemberRole.OWNER
        )
    )
    await db.commit()
    
    return ChannelResponse(
        id=str(channel.id),
        name=channel.name,
        description=channel.description,
        type=channel.type,
        owner_id=str(channel.owner_id),
        created_at=channel.created_at
    )

@router.get("/", response_model=List[ChannelResponse])
async def list_channels(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Channel).where(Channel.is_active == True)
    )
    channels = result.scalars().all()
    
    return [
        ChannelResponse(
            id=str(ch.id),
            name=ch.name,
            description=ch.description,
            type=ch.type,
            owner_id=str(ch.owner_id),
            created_at=ch.created_at
        )
        for ch in channels
    ]

@router.post("/{channel_id}/members")
async def add_channel_member(
    channel_id: str,
    member_data: ChannelMemberAdd,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user has permission (owner/admin)
    await db.execute(
        insert(channel_members).values(
            channel_id=channel_id,
            user_id=member_data.user_id,
            role=member_data.role
        )
    )
    await db.commit()
    return {"message": "Member added successfully"}

@router.delete("/{channel_id}/members/{user_id}")
async def remove_channel_member(
    channel_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await db.execute(
        delete(channel_members).where(
            channel_members.c.channel_id == channel_id,
            channel_members.c.user_id == user_id
        )
    )
    await db.commit()
    return {"message": "Member removed successfully"}
