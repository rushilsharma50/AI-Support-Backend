from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketResponse, TicketHistoryResponse
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_in: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new support ticket."""
    return await TicketService.create_ticket(db, ticket_in, current_user)


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tickets with optional filtering and pagination."""
    return await TicketService.list_tickets(
        db,
        ticket_status=status_filter,
        priority=priority,
        category=category,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single ticket by ID."""
    return await TicketService.get_ticket(db, ticket_id)


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a ticket. Only the ticket creator can update."""
    return await TicketService.update_ticket(db, ticket_id, ticket_in, current_user)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a ticket. Only the ticket creator can delete."""
    await TicketService.delete_ticket(db, ticket_id, current_user)


@router.get("/{ticket_id}/history", response_model=list[TicketHistoryResponse])
async def get_ticket_history(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the audit history for a ticket."""
    return await TicketService.get_ticket_history(db, ticket_id)
