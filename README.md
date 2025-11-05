# AI Coach Agent – Telex A2A + FastAPI + Gemini

This project implements a **Multi‑Modal AI Coaching Agent** connected to **Telex.im** using the **A2A protocol**, with:

* Gemini LLM for smart coaching
* FastAPI A2A RPC endpoint
* HMAC request signature verification
* Background worker (task queue)
* Docker + docker‑compose setup

## Features

| Feature                     | Description                                          |
| --------------------------- | ---------------------------------------------------- |
| A2A FastAPI endpoint        | Responds to Telex agent messages                     |
| Gemini LLM                  | Smart coaching for learning & productivity           |
| Background worker           | Handles offline coaching recommendations & reminders |
| HMAC Signature verification | Secures Telex → Agent calls                          |
| Dockerized                  | Easy deployment                                      |

## Requirements

```bash
Python 3.10+
Docker & Docker Compose
Telex.im account
Gemini API Key
```

## Environment Variables

Create `.env` file in the core directory:

```bash
AGENT_SIGNING_SECRET=shared_secret_with_telex
TELEX_AGENT_ID=agent-id-here
PROJECT_NAME=Multi-Modal Coach Agent (A2A)
APP_VERSION="0.1.0"
ALLOWED_ORIGINS=
SECRET_KEY="SECRET_KEY"
ENV="local"
POSTGRES_USER="db user"
POSTGRES_PASSWORD="db password"
POSTGRES_HOST="localhost"
POSTGRES_PORT="5432"
POSTGRES_DB="db name"
DATABASE_UR="postgresql+psycopg2://your_pass:your_db_name@localhost:5432/agent"
GEMINI_API_KEY="your gemini api key"
TELEX_LOG_BASE="https://api.telex.im/agent-logs"
LOG_PATH="agent_interactions.log"
AGENT_API_KEY=lllll
```

## Running with Docker

### Build + Start

```bash
docker compose up --build -d
```

### Check logs

```bash
docker logs ai-coach-app -f
docker logs ai-coach-worker -f
```

### Stop

```bash
docker-compose down
```

## Running Locally

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
git clone https://github.com/triplee12/a2a-Coach.git
cd a2a-Coach
pip install -r requirements.txt
```

### 2. Run FastAPI API

```bash
uvicorn agent.main:app --reload --port 8000

# Or

python -m agent.main
```

### 3. Run background worker

```bash
python agent/core/worker.py
```

## Telex A2A Configuration

Add your agent endpoint in Telex under A2A node:

```text
https://your-server.com/rpc
```

Make sure Telex sends headers:

```text
X-A2A-Signature
X-A2A-Timestamp
```

## Verify it's working

### Health

```text
GET http://localhost:8000/a2a-coach/health/status
```

Response:

```json
{"status": "ok"}
```

### A2A Test

Send a JSON‑RPC message:

```bash
curl -X POST http://localhost:8000/a2a-coach/rpc -H "Content-Type: application/json" -d '{
  "jsonrpc":"2.0",
  "method":"tasks/send",
  "params": {
    "context_id":"session_123",
    "sender":"telex-user-001",
    "task": {
      "id":"t1",
      "title":"Learn Golang in 8 weeks",
      "type":"planning",
      "parts":[{"text":"I want a Go roadmap and project ideas to help me achieve more experiences in each step from beginner to advanced. Also a progress tracking"}]
    }
  },
  "id":"req1"
}'
```

Send Telex WebHook message:

```bash
curl -X POST http://localhost:8000/a2a-coach/coach -H "Content-Type: application/json" -d '{
  "id": "session_12345",
  "message": "Help me design a 30-day Python learning roadmap",
  "sender": "telex-user-001",
  "channel_id": "channel_abc123",
  "workflow_id": "workflow_001"
}'
```

## Project Structure

```text
agent/
 ├─ api/
 ├─ core/
 ├─ db/
 ├─ models/
 ├─ services/
 ├─ main.py (FastAPI entry)
 ├─ Dockerfile
 ├─ docker-compose.yml
 ├─ .gitignore
 ├─ alembic.ini
 ├─ requirements.txt
 ├─ .env
```

## Security

* HMAC SHA‑256 signature enforcement
* Timestamp + replay attack protection
* `.env` secrets required

## Debug Logs

View real log stream:

```text
https://api.telex.im/agent-logs/{channel-id}.txt
```

## Support

**Need help?** DM me or ask inside Telex community.

Happy hacking!
