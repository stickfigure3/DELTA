# DELTA Deployment Guide

## Quick Deploy Options (No EID/Verification Required)

### Option 1: Railway.app (Recommended - Easiest)

1. **Sign up** at https://railway.app (use GitHub login)

2. **Create new project** → "Deploy from GitHub repo"

3. **Select** `stickfigure3/DELTA`

4. **Add environment variables:**
   ```
   SECRET_KEY=<generate-random-32-char-string>
   JWT_SECRET_KEY=<generate-random-32-char-string>
   DATABASE_URL=sqlite+aiosqlite:///./delta.db
   ENVIRONMENT=production
   DEBUG=false
   ```

5. **Deploy!** Railway will auto-detect the Dockerfile

6. **Get your URL:** Something like `delta-production.up.railway.app`

---

### Option 2: Render.com

1. **Sign up** at https://render.com (use GitHub login)

2. **New** → **Web Service** → Connect GitHub repo

3. **Select** `stickfigure3/DELTA`

4. **Settings:**
   - Name: `delta-api`
   - Region: Oregon (closest to Bay Area)
   - Branch: `main`
   - Root Directory: (leave blank)
   - Runtime: Docker
   - Instance Type: Free

5. **Environment Variables:**
   ```
   SECRET_KEY=<generate-random-32-char-string>
   JWT_SECRET_KEY=<generate-random-32-char-string>
   DATABASE_URL=sqlite+aiosqlite:///./delta.db
   ```

6. **Create Web Service**

---

## After Deployment

### Test the API

```bash
# Replace with your actual URL
export DELTA_URL="https://your-app.railway.app"

# Health check
curl $DELTA_URL/health

# API info
curl $DELTA_URL/
```

### Connect an Agent

```python
import asyncio
import websockets
import json

DELTA_URL = "wss://your-app.railway.app"  # Use wss:// for HTTPS
AGENT_ID = "my-agent-123"
API_KEY = "my-api-key"

async def agent():
    uri = f"{DELTA_URL}/v1/ws/agent/{AGENT_ID}?api_key={API_KEY}"
    
    async with websockets.connect(uri) as ws:
        # Send message to users
        await ws.send(json.dumps({
            "type": "message",
            "content": "Hello from the cloud!",
        }))
        
        # Listen for user messages
        async for msg in ws:
            print(f"User said: {json.loads(msg)}")

asyncio.run(agent())
```

### Connect as User (Browser)

```javascript
// In browser console or JavaScript
const ws = new WebSocket(
  "wss://your-app.railway.app/v1/ws/user/my-agent-123?user_id=user-456"
);

ws.onmessage = (event) => {
  console.log("Agent says:", JSON.parse(event.data));
};

// Send message to agent
ws.send(JSON.stringify({
  type: "message",
  content: "Hello agent!"
}));
```

---

## WebSocket Endpoints

| Endpoint | Who Uses It | Purpose |
|----------|-------------|---------|
| `/v1/ws/user/{agent_id}?user_id=X` | Users | Watch agent, send messages |
| `/v1/ws/agent/{agent_id}?api_key=X` | Agents | Send messages to users |
| `/v1/ws/stats` | Admin | Connection statistics |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOUD (Railway/Render)                    │
│                                                              │
│   ┌────────────────────────────────────────────────────┐    │
│   │                  DELTA API Server                   │    │
│   │                                                     │    │
│   │   ┌─────────────┐    ┌─────────────────────────┐  │    │
│   │   │  REST API   │    │  WebSocket Manager      │  │    │
│   │   │  /v1/*      │    │                         │  │    │
│   │   └─────────────┘    │  Agent ←→ User Comms   │  │    │
│   │                      │                         │  │    │
│   │                      │  • Message routing      │  │    │
│   │                      │  • Connection tracking  │  │    │
│   │                      │  • History storage      │  │    │
│   │                      └─────────────────────────┘  │    │
│   └────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
       ┌─────────────┐              ┌─────────────┐
       │  AI AGENT   │              │    USER     │
       │  (Claude,   │              │  (Browser,  │
       │   GPT, etc) │              │   App)      │
       │             │              │             │
       │ Connects to │              │ Connects to │
       │ /ws/agent/* │              │ /ws/user/*  │
       └─────────────┘              └─────────────┘
```

---

## Team Tasks (Parallel Development)

While you deploy the core platform, your team can work on:

| Task | Owner | Integration Point |
|------|-------|-------------------|
| Twilio (SMS/Calls) | Team | `POST /v1/messaging/sms` |
| AWS SES (Email) | Team | `POST /v1/messaging/email` |
| Stripe (Payments) | Team | `/v1/billing/*` (to be added) |
| User Registration | Team | `POST /v1/auth/register` |

Each integration is independent and can be developed in parallel.

---

## Generate Secure Keys

```bash
# Generate 32-char random strings for SECRET_KEY and JWT_SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Support

- **GitHub**: https://github.com/stickfigure3/DELTA
- **Google Doc**: https://docs.google.com/document/d/1lGc8EZbQq5pW0jq3Lgl95sk9RQMQiHCXZjQMIdIdP98/edit
