# AdaptLab

**Adaptive AI-Powered C Programming Tutor with Socratic Guidance**

AdaptLab is a multi-agent Socratic AI tutor for adaptive C programming education. It uses three specialized AI agents (Teacher, Generator, Socratic) powered by the Kimi API to create a personalized learning experience. The system adapts to each student's strengths and weaknesses through a knowledge graph and capability matrix, generating tailored problems, executing code in a sandboxed environment, and providing guided hints that help students think through their mistakes without ever revealing the answer.

## Architecture

```
┌─────────────┐      ┌──────────────────────────────────────┐
│             │      │            FastAPI Backend             │
│   React     │ /api │  ┌─────────┐  ┌───────────┐          │
│   Frontend  │─────▶│  │ Teacher │  │ Generator │          │
│   (nginx)   │      │  │  Agent  │  │   Agent   │          │
│   :3000     │      │  └────┬────┘  └─────┬─────┘          │
│             │      │       │              │                │
└─────────────┘      │  ┌────▼──────────────▼─────┐         │
                     │  │   Adaptive Loop Service  │         │
                     │  └────┬──────────────┬──────┘         │
                     │       │              │                │
                     │  ┌────▼────┐   ┌─────▼──────┐        │
                     │  │Socratic │   │  Knowledge │        │
                     │  │  Agent  │   │   Graph    │        │
                     │  └─────────┘   │ (NetworkX) │        │
                     │                └────────────┘        │
                     └──────┬───────────────┬───────────────┘
                            │               │
                     ┌──────▼──────┐ ┌──────▼──────┐
                     │ PostgreSQL  │ │  Judge0 CE  │
                     │   :5432     │ │   :2358     │
                     └─────────────┘ └─────────────┘
                                            │
                                     ┌──────▼──────┐
                                     │  Kimi API   │
                                     │ moonshot.cn │
                                     └─────────────┘
```

## Prerequisites

- **Docker** and **Docker Compose** (v2+)
- A **Kimi API key** from [Moonshot AI Platform](https://platform.moonshot.cn/)
- At least 4GB RAM available for Docker

## Quick Start

```bash
# Clone the repository
git clone <repo-url>
cd adaptlab

# Set up environment
cp .env.example .env
# Edit .env and add your KIMI_API_KEY

# Build and launch all services
docker compose up --build

# Visit http://localhost:3000
```

The first startup takes a few minutes as Docker pulls images and builds containers. Judge0 CE may take extra time to initialize its compiler toolchain.

## Default Ports

| Service    | Port | Description                    |
|------------|------|--------------------------------|
| Frontend   | 3000 | React app served via nginx     |
| Backend    | 8000 | FastAPI + uvicorn              |
| PostgreSQL | 5432 | AdaptLab database              |
| Judge0 CE  | 2358 | Code execution sandbox (internal) |

## Project Structure

```
adaptlab/
├── docker-compose.yml          # All services orchestration
├── .env.example                # Environment variables template
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini             # Database migration config
│   ├── alembic/                # Migration scripts
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── config.py           # Pydantic settings
│   │   ├── database.py         # Async SQLAlchemy setup
│   │   ├── models/             # SQLAlchemy models (User, Session)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── routers/            # API route handlers
│   │   ├── agents/             # Kimi API agents (Teacher, Generator, Socratic)
│   │   ├── engine/             # Knowledge graph + code executor
│   │   └── services/           # Adaptive loop + capability matrix
│   └── curriculum/             # Obsidian-style markdown concept files
├── frontend/
│   ├── Dockerfile              # Multi-stage build (node → nginx)
│   ├── nginx.conf              # Reverse proxy config
│   ├── src/
│   │   ├── App.jsx             # Root component with routing
│   │   ├── api/client.js       # Axios API client
│   │   ├── hooks/              # useAuth, useSession
│   │   ├── components/         # Reusable UI components
│   │   └── pages/              # Login, Session, Dashboard
│   └── ...config files
```

## Adding New Concepts

To add a new C programming concept to the curriculum:

1. Create a new `.md` file in `backend/curriculum/`:

```markdown
---
id: your_concept_id
title: Your Concept Title
level: 3
prerequisites: [existing_concept_id]
unlocks: [another_concept_id]
---

Brief description of the concept.
```

2. Update any existing concepts that should list this as a prerequisite or unlock.
3. Restart the backend — the knowledge graph is rebuilt on startup.
4. The system automatically includes new concepts in the capability matrix for new users.

## Environment Variables

| Variable         | Description                          | Default                              |
|------------------|--------------------------------------|--------------------------------------|
| `DATABASE_URL`   | PostgreSQL connection string         | `postgresql+asyncpg://adaptlab:adaptlab@db:5432/adaptlab` |
| `KIMI_API_KEY`   | Moonshot AI API key                  | *(required)*                         |
| `KIMI_MODEL`     | Kimi model name                      | `moonshot-v1-8k`                     |
| `JWT_SECRET`     | Secret key for JWT signing           | *(change in production)*             |
| `JWT_ALGORITHM`  | JWT signing algorithm                | `HS256`                              |
| `JWT_EXPIRY_HOURS` | Token expiration time              | `24`                                 |
| `JUDGE0_URL`     | Judge0 CE endpoint                   | `http://judge0:2358`                 |
| `CORS_ORIGINS`   | Allowed CORS origins (comma-separated) | `http://localhost:5173,http://localhost:3000` |

## API Endpoints

| Method | Path                          | Description                       |
|--------|-------------------------------|-----------------------------------|
| POST   | `/api/auth/register`          | Register a new user               |
| POST   | `/api/auth/login`             | Login and get JWT token           |
| GET    | `/api/auth/me`                | Get current user profile          |
| POST   | `/api/session/start`          | Start a new tutoring session      |
| POST   | `/api/session/{id}/submit`    | Submit code for evaluation        |
| GET    | `/api/session/{id}`           | Get session details               |
| POST   | `/api/session/{id}/next`      | Start next problem                |
| GET    | `/api/progress`               | Get full progress report          |
| GET    | `/api/progress/graph`         | Get knowledge graph with mastery  |
| GET    | `/api/submissions/history`    | Get paginated submission history  |
| GET    | `/api/health`                 | Health check                      |

## Technology Stack

| Component        | Technology                    | Purpose                          |
|------------------|-------------------------------|----------------------------------|
| Frontend         | React (Vite), Tailwind CSS    | Modern, responsive UI            |
| Code Editor      | Monaco Editor                 | In-browser C code editing        |
| Backend          | FastAPI (Python 3.11)         | Async REST API                   |
| AI Agents        | Kimi API (Moonshot AI)        | Teacher, Generator, Socratic     |
| Knowledge Graph  | NetworkX + YAML Markdown      | Curriculum DAG                   |
| Database         | PostgreSQL 15 + SQLAlchemy 2  | User data + session storage      |
| Code Sandbox     | Judge0 CE (self-hosted)       | Secure C compilation & execution |
| Containerization | Docker Compose                | Single-command deployment        |

## License

MIT
