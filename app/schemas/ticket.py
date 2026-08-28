from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enums import TicketStatus, TicketPriority, TicketCategory, TicketSentiment

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: TicketPriority = TicketPriority.MEDIUM
    category: Optional[TicketCategory] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    assigned_to: Optional[int] = None

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    category: Optional[str] = None
    sentiment: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_suggested_response: Optional[str] = None
    created_by: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
