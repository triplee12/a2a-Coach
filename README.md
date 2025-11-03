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

```
Python 3.10+
Docker & Docker Compose
Telex.im account
Gemini API Key
```

## Environment Variables

Create `.env` file:

```
GEMINI_API_KEY=your_gemini_key_here
AGENT_SIGNING_SECRET=shared_secret_with_telex
TELEX_AGENT_ID=agent-id-here
```

## Running with Docker

### Build + Start

```bash
docker-compose up --build -d
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
pip install -r requirements.txt
```

### 2. Run FastAPI API

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Run background worker

```bash
python app/worker.py
```

## Telex A2A Configuration

Add your agent endpoint in Telex under A2A node:

```
https://your-server.com/rpc
```

Make sure Telex sends headers:

```
X-A2A-Signature
X-A2A-Timestamp
```

## Verify it's working

### Health

```
GET http://localhost:8000/status
```

Response:

```json
{"status": "ok"}
```

### A2A Test

Send a JSON‑RPC message:

```bash
curl -X POST http://localhost:8000/rpc \
 -H "Content-Type: application/json" \
 -d '{"id":1, "method":"coach.ask", "params":{"message":"I want to learn Python"}}'
```

## Project Structure

```
app/
 ├─ main.py (FastAPI entry)
 ├─ a2a_routes.py
 ├─ gemini_client.py
 ├─ coach_service.py
 ├─ worker.py
 ├─ utils.py (signature verification)
Dockerfile
docker-compose.yml
.env
```

## Security

* HMAC SHA‑256 signature enforcement
* Timestamp + replay attack protection
* `.env` secrets required

## Debug Logs

View real log stream:

```
https://api.telex.im/agent-logs/{channel-id}.txt
```

## Support

**Need help?** DM me or ask inside Telex community.

Happy hacking!
