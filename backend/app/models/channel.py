from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum
from app.core.database import Base

class ChannelType(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    DIRECT = "direct"
    GROUP = "group"

class MemberRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"

channel_members = Table(
    "channel_members",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("channel_id", UUID(as_uuid=True), ForeignKey("channels.id", ondelete="CASCADE")),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")),
    Column("role", Enum(MemberRole), default=MemberRole.MEMBER),
    Column("joined_at", DateTime, default=datetime.utcnow)
)

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(Enum(ChannelType), default=ChannelType.PUBLIC)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
