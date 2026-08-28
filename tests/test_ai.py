"""Tests for the AI ticket analysis endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.ai import TicketAnalysis
from app.models.enums import TicketCategory, TicketPriority, TicketSentiment

# A canned analysis result used by the mock
MOCK_ANALYSIS = TicketAnalysis(
    category=TicketCategory.BILLING,
    priority=TicketPriority.HIGH,
    sentiment=TicketSentiment.NEGATIVE,
    summary="Customer was charged twice for a single order.",
    suggested_response="We apologise for the inconvenience. We will look into the duplicate charge and get back to you shortly.",
)


# --- helpers ---

async def _create_ticket(client: AsyncClient, auth_headers: dict) -> int:
    """Create a ticket and return its ID."""
    resp = await client.post(
        "/api/tickets",
        json={"title": "Double charge", "description": "I was charged twice for order #1234."},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


# --- tests ---

@pytest.mark.asyncio
async def test_analyze_unauthenticated(client: AsyncClient):
    response = await client.post("/api/tickets/1/analyze")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_ticket_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.post("/api/tickets/9999/analyze", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
@patch("app.services.ai_service.analyse_ticket", new_callable=AsyncMock, return_value=MOCK_ANALYSIS)
async def test_analyze_ticket_success(mock_ai, client: AsyncClient, auth_headers: dict):
    ticket_id = await _create_ticket(client, auth_headers)

    response = await client.post(f"/api/tickets/{ticket_id}/analyze", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["category"] == "BILLING"
    assert data["priority"] == "HIGH"
    assert data["sentiment"] == "NEGATIVE"
    assert data["ai_summary"] == MOCK_ANALYSIS.summary
    assert data["ai_suggested_response"] == MOCK_ANALYSIS.suggested_response

    # Verify the mock was called
    mock_ai.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.ai_service.analyse_ticket", new_callable=AsyncMock, side_effect=Exception("upstream failure"))
async def test_analyze_ticket_ai_failure(mock_ai, client: AsyncClient, auth_headers: dict):
    ticket_id = await _create_ticket(client, auth_headers)

    response = await client.post(f"/api/tickets/{ticket_id}/analyze", headers=auth_headers)
    assert response.status_code == 502
    assert "unavailable" in response.json()["detail"].lower()
