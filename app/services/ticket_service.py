from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from typing import Optional

from app.models.ticket import Ticket
from app.models.ticket_history import TicketHistory
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate


class TicketService:
    # --- History helpers ---

    @staticmethod
    async def _add_history(
        db: AsyncSession, ticket_id: int, user_id: int,
        action: str, old_value: str | None = None, new_value: str | None = None,
    ):
        entry = TicketHistory(
            ticket_id=ticket_id,
            user_id=user_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
        )
        db.add(entry)

    # --- CRUD ---

    @staticmethod
    async def create_ticket(db: AsyncSession, ticket_in: TicketCreate, user: User) -> Ticket:
        ticket = Ticket(
            title=ticket_in.title,
            description=ticket_in.description,
            priority=ticket_in.priority.value,
            category=ticket_in.category.value if ticket_in.category else None,
            created_by=user.id,
        )
        db.add(ticket)
        await db.flush()  # get the ticket.id before creating history

        await TicketService._add_history(db, ticket.id, user.id, "ticket_created")
        await db.commit()
        await db.refresh(ticket)
        return ticket

    @staticmethod
    async def get_ticket(db: AsyncSession, ticket_id: int) -> Ticket:
        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        return ticket

    @staticmethod
    async def list_tickets(
        db: AsyncSession, *,
        ticket_status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Ticket]:
        query = select(Ticket)

        if ticket_status:
            query = query.where(Ticket.status == ticket_status)
        if priority:
            query = query.where(Ticket.priority == priority)
        if category:
            query = query.where(Ticket.category == category)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(Ticket.title.ilike(pattern), Ticket.description.ilike(pattern))
            )

        query = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_ticket(
        db: AsyncSession, ticket_id: int, ticket_in: TicketUpdate, user: User
    ) -> Ticket:
        ticket = await TicketService.get_ticket(db, ticket_id)

        # Authorization: only the creator can update
        if ticket.created_by != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        update_data = ticket_in.model_dump(exclude_unset=True)

        # Track changes for history
        for field, new_value in update_data.items():
            old_value = getattr(ticket, field)
            # Convert enums to their string value for comparison/storage
            new_value_str = new_value.value if hasattr(new_value, "value") else str(new_value) if new_value is not None else None
            old_value_str = str(old_value) if old_value is not None else None

            if old_value_str != new_value_str:
                await TicketService._add_history(
                    db, ticket.id, user.id,
                    action=f"{field}_changed",
                    old_value=old_value_str,
                    new_value=new_value_str,
                )
                setattr(ticket, field, new_value_str)

        await db.commit()
        await db.refresh(ticket)
        return ticket

    @staticmethod
    async def delete_ticket(db: AsyncSession, ticket_id: int, user: User) -> None:
        ticket = await TicketService.get_ticket(db, ticket_id)

        if ticket.created_by != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        # Delete history entries first (they reference the ticket via FK)
        from sqlalchemy import delete as sa_delete
        await db.execute(
            sa_delete(TicketHistory).where(TicketHistory.ticket_id == ticket_id)
        )
        await db.delete(ticket)
        await db.commit()

    @staticmethod
    async def get_ticket_history(db: AsyncSession, ticket_id: int) -> list[TicketHistory]:
        # Ensure ticket exists
        await TicketService.get_ticket(db, ticket_id)
        result = await db.execute(
            select(TicketHistory)
            .where(TicketHistory.ticket_id == ticket_id)
            .order_by(TicketHistory.created_at)
        )
        return list(result.scalars().all())
