from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from app.database.database import Base
from app.models.enums import TicketStatus, TicketPriority, TicketCategory, TicketSentiment

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.ticket_history import TicketHistory

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=TicketStatus.OPEN.value)
    priority: Mapped[str] = mapped_column(String(20), default=TicketPriority.MEDIUM.value)
    category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sentiment: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ai_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_suggested_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to])
    history: Mapped[list["TicketHistory"]] = relationship("TicketHistory", back_populates="ticket")
