# Bozorchi

Telegram marketplace bot.

## Tech Stack

- Python 3.13+
- aiogram 3.x
- PostgreSQL
- Redis
- SQLAlchemy
- Alembic
- APScheduler
- FastAPI
- Docker

## Project Structure

```text
bozorchi/
├── app/
│   ├── core/
│   ├── db/
│   ├── cache/
│   ├── bot/
│   ├── services/
│   └── workers/
│
├── api/
├── tests/
├── alembic/
├── docker/
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
