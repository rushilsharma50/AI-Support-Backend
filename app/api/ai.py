import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.ai import TicketAnalysis
from app.schemas.ticket import TicketResponse
from app.services.ticket_service import TicketService
from app.services import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tickets", tags=["AI"])


@router.post("/{ticket_id}/analyze", response_model=TicketResponse)
async def analyze_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run AI analysis on a ticket and persist the results."""
    ticket = await TicketService.get_ticket(db, ticket_id)

    try:
        analysis: TicketAnalysis = await ai_service.analyse_ticket(
            title=ticket.title,
            description=ticket.description,
        )
    except RuntimeError as exc:
        # Missing API key
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except (ValueError, KeyError) as exc:
        # Malformed model response
        logger.error("AI returned invalid response: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned an invalid response",
        )
    except Exception as exc:
        # Upstream API failure
        logger.error("AI service error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service is currently unavailable",
        )

    # Persist analysis results on the ticket
    ticket.category = analysis.category.value
    ticket.priority = analysis.priority.value
    ticket.sentiment = analysis.sentiment.value
    ticket.ai_summary = analysis.summary
    ticket.ai_suggested_response = analysis.suggested_response

    # Record AI analysis in ticket history
    await TicketService._add_history(
        db, ticket.id, current_user.id,
        action="ai_analysis",
        new_value=f"category={analysis.category.value}, priority={analysis.priority.value}, sentiment={analysis.sentiment.value}",
    )

    await db.commit()
    await db.refresh(ticket)
    return ticket
