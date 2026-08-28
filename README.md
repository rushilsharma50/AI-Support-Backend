# AI Support Backend & Dashboard

## Overview
AI-powered customer support ticket management system built with **FastAPI**, **React**, **PostgreSQL**, and **Google Gemini AI**. 

The platform provides a complete REST API and a modern SaaS dashboard for managing support tickets. It features AI-powered analysis that automatically categorizes, prioritizes, and evaluates the sentiment of support requests, alongside suggesting professional customer responses.

## Features
- **JWT Authentication**: Register, login, and protected routes
- **Support Ticket Management**: Full CRUD operations
- **Ticket Search/Filtering**: Find tickets by status, priority, category, or keyword
- **Ticket History**: Automatic audit log of changes (status, priority, AI analysis)
- **AI Ticket Classification**: Gemini AI automatically categorizes tickets (Billing, Technical, etc.)
- **AI Priority Assessment**: Determines if a ticket is Low, Medium, High, or Urgent
- **Sentiment Analysis**: Evaluates customer sentiment (Positive, Neutral, Negative)
- **AI Summarization**: Generates a concise summary of the issue
- **Suggested Customer Response**: Drafts a professional reply based on the issue
- **PostgreSQL Persistence**: Fully asynchronous database operations
- **API Documentation**: Auto-generated Swagger UI

## Architecture

```mermaid
graph TD
    User([User]) --> |React/Vite| Frontend[Frontend Dashboard]
    Frontend --> |HTTP/JWT| FastAPI[FastAPI Backend]
    
    subgraph Backend
        FastAPI --> Auth[Authentication]
        FastAPI --> TicketSvc[Ticket Service]
        FastAPI --> History[Ticket History]
        FastAPI --> AISvc[AI Service]
    end
    
    TicketSvc --> DB[(PostgreSQL)]
    History --> DB
    Auth --> DB
    
    AISvc --> |System Prompt + Ticket Text| Gemini[Google Gemini AI]
    Gemini --> |Structured JSON| AISvc
```

### Why Structured AI Output?
The AI integration leverages Google Gemini with strict Pydantic schemas. Instead of relying on unpredictable free-form text, the backend enforces structured JSON output. This ensures the AI reliably populates Enums (Category, Priority, Sentiment) which are easily queryable in the database and rendering in the dashboard.

## Technology Stack

**Frontend:**
- React 18
- TypeScript
- Vite
- React Router DOM
- Tailwind CSS
- Lucide React (Icons)

**Backend:**
- Python 3.12+
- FastAPI
- SQLAlchemy 2.x (Async)
- asyncpg (PostgreSQL driver)
- Pydantic v2
- Alembic (Migrations)
- JWT (python-jose) + Argon2

**AI:**
- Google Gemini API (`google-genai` SDK)

**Testing & Infra:**
- pytest + aiosqlite

## Project Structure

```
├── app/                  # FastAPI Backend
│   ├── api/              # Route handlers (auth, tickets, ai)
│   ├── core/             # Config & Security
│   ├── database/         # Async engine setup
│   ├── models/           # SQLAlchemy models & Enums
│   ├── schemas/          # Pydantic validation schemas
│   └── services/         # Business logic & AI integration
├── frontend/             # React Dashboard
│   ├── src/
│   │   ├── components/   # Layout, Sidebar, Protected Routes
│   │   ├── pages/        # Login, Dashboard, Ticket views
│   │   ├── api.ts        # Fetch wrapper with auth interceptor
│   │   └── AuthContext.tsx # Global authentication state
│   ├── tailwind.config.js
│   └── vite.config.ts
├── tests/                # Pytest suites
```

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd ai-support-backend
```

### 2. Backend Setup
Create a Python virtual environment and install dependencies:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Backend Environment Configuration
```bash
cp .env.example .env
```
Edit `.env` to configure your PostgreSQL credentials and Gemini API Key:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/support_db
SECRET_KEY=your_super_secret_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run PostgreSQL & Migrations
Ensure PostgreSQL is running locally and the `support_db` database exists.
Run Alembic migrations to create tables:
```bash
alembic upgrade head
```

### 5. Start the FastAPI Backend
```bash
fastapi dev app/main.py
```
The backend API is now running at `http://127.0.0.1:8000`. Swagger docs at `/docs`.

### 6. Frontend Setup
Open a new terminal and install frontend dependencies:
```bash
cd frontend
npm install
```

### 7. Frontend Environment Configuration
```bash
cp .env.example .env
```
Ensure `frontend/.env` points to your backend:
```env
VITE_API_URL=http://127.0.0.1:8000
```

### 8. Start the React Frontend
```bash
npm run dev
```
The dashboard is now running at `http://localhost:5173`.

## Testing

Backend tests are written with `pytest` and use an in-memory SQLite database, requiring no active Postgres or Gemini API key.

```bash
pip install aiosqlite pytest-asyncio
pytest tests/ -v
```

## API Summary

- **Auth:** `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- **Tickets:** `POST /api/tickets`, `GET /api/tickets`, `GET /api/tickets/{id}`, `PUT /api/tickets/{id}`, `DELETE /api/tickets/{id}`
- **History:** `GET /api/tickets/{id}/history`
- **AI:** `POST /api/tickets/{id}/analyze`

## Future Improvements

- **Role-Based Access Control**: Differentiate between Support Agents and Customers.
- **Real-Time Notifications**: Use WebSockets for live updates when tickets are modified.
- **Batch AI Analysis**: Analyze multiple tickets asynchronously.
- **Extended Dashboard Metrics**: Include resolution times and agent performance.

---

## Screenshots

### Login
<!-- Add Screenshot here: ![Login Screen](docs/login.png) -->

### Dashboard
<!-- Add Screenshot here: ![Dashboard](docs/dashboard.png) -->

### Ticket List
<!-- Add Screenshot here: ![Ticket List](docs/ticket_list.png) -->

### Ticket Details & History
<!-- Add Screenshot here: ![Ticket Details](docs/ticket_details.png) -->

### AI Analysis Results
<!-- Add Screenshot here: ![AI Analysis](docs/ai_analysis.png) -->
