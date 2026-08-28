import pytest
from httpx import AsyncClient

# ---- Create ----

@pytest.mark.asyncio
async def test_create_ticket(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/tickets",
        json={"title": "Billing issue", "description": "I was double charged", "priority": "HIGH", "category": "BILLING"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Billing issue"
    assert data["status"] == "OPEN"
    assert data["priority"] == "HIGH"
    assert data["category"] == "BILLING"


@pytest.mark.asyncio
async def test_create_ticket_unauthenticated(client: AsyncClient):
    response = await client.post(
        "/api/tickets",
        json={"title": "No auth", "description": "Should fail"},
    )
    assert response.status_code == 401


# ---- Get ----

@pytest.mark.asyncio
async def test_get_ticket(client: AsyncClient, auth_headers: dict):
    # Create first
    create_resp = await client.post(
        "/api/tickets",
        json={"title": "Get me", "description": "desc"},
        headers=auth_headers,
    )
    ticket_id = create_resp.json()["id"]

    response = await client.get(f"/api/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


@pytest.mark.asyncio
async def test_get_ticket_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/tickets/9999", headers=auth_headers)
    assert response.status_code == 404


# ---- List ----

@pytest.mark.asyncio
async def test_list_tickets(client: AsyncClient, auth_headers: dict):
    await client.post("/api/tickets", json={"title": "T1", "description": "d1"}, headers=auth_headers)
    await client.post("/api/tickets", json={"title": "T2", "description": "d2"}, headers=auth_headers)

    response = await client.get("/api/tickets", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


# ---- Filtering ----

@pytest.mark.asyncio
async def test_filter_by_status(client: AsyncClient, auth_headers: dict):
    await client.post("/api/tickets", json={"title": "Open ticket", "description": "d"}, headers=auth_headers)

    response = await client.get("/api/tickets?status_filter=OPEN", headers=auth_headers)
    assert response.status_code == 200
    for ticket in response.json():
        assert ticket["status"] == "OPEN"


@pytest.mark.asyncio
async def test_filter_by_priority(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/tickets",
        json={"title": "Urgent", "description": "d", "priority": "URGENT"},
        headers=auth_headers,
    )

    response = await client.get("/api/tickets?priority=URGENT", headers=auth_headers)
    assert response.status_code == 200
    for ticket in response.json():
        assert ticket["priority"] == "URGENT"


@pytest.mark.asyncio
async def test_search_tickets(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/tickets",
        json={"title": "Payment refund needed", "description": "overcharged"},
        headers=auth_headers,
    )

    response = await client.get("/api/tickets?search=payment", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert "payment" in response.json()[0]["title"].lower()


# ---- Update ----

@pytest.mark.asyncio
async def test_update_ticket(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/tickets",
        json={"title": "To update", "description": "d"},
        headers=auth_headers,
    )
    ticket_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/tickets/{ticket_id}",
        json={"status": "IN_PROGRESS", "priority": "URGENT"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_PROGRESS"
    assert data["priority"] == "URGENT"


# ---- Delete ----

@pytest.mark.asyncio
async def test_delete_ticket(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/tickets",
        json={"title": "To delete", "description": "d"},
        headers=auth_headers,
    )
    ticket_id = create_resp.json()["id"]

    response = await client.delete(f"/api/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify gone
    get_resp = await client.get(f"/api/tickets/{ticket_id}", headers=auth_headers)
    assert get_resp.status_code == 404


# ---- History ----

@pytest.mark.asyncio
async def test_ticket_history_on_create(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/tickets",
        json={"title": "History test", "description": "d"},
        headers=auth_headers,
    )
    ticket_id = create_resp.json()["id"]

    response = await client.get(f"/api/tickets/{ticket_id}/history", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert history[0]["action"] == "ticket_created"


@pytest.mark.asyncio
async def test_ticket_history_on_update(client: AsyncClient, auth_headers: dict):
    create_resp = await client.post(
        "/api/tickets",
        json={"title": "History update", "description": "d"},
        headers=auth_headers,
    )
    ticket_id = create_resp.json()["id"]

    await client.put(
        f"/api/tickets/{ticket_id}",
        json={"status": "RESOLVED"},
        headers=auth_headers,
    )

    response = await client.get(f"/api/tickets/{ticket_id}/history", headers=auth_headers)
    history = response.json()
    actions = [h["action"] for h in history]
    assert "status_changed" in actions
