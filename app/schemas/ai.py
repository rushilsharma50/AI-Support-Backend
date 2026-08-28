from pydantic import BaseModel
from app.models.enums import TicketCategory, TicketPriority, TicketSentiment


class TicketAnalysis(BaseModel):
    """Structured AI analysis result for a support ticket."""
    category: TicketCategory
    priority: TicketPriority
    sentiment: TicketSentiment
    summary: str
    suggested_response: str
