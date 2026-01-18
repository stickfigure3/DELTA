# DELTA - Dynamic Environment for LLM Task Automation

> **Version 0.1** | Cloud-based sandbox-as-a-service for self-improving LLM agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Project Documentation

**Master Planning Document**: [Google Doc - DELTA Project Spec](https://docs.google.com/document/d/1lGc8EZbQq5pW0jq3Lgl95sk9RQMQiHCXZjQMIdIdP98/edit?tab=t.0)

---

## 🎯 What is DELTA?

DELTA is a cloud-based sandbox-as-a-service platform that gives LLM agents secure, isolated environments to execute code, run terminal commands, and manage files—all accessible via a simple API.

**Key Differentiator**: DELTA environments are **self-improving**—the LLM can install packages, create custom scripts, and modify its own tooling, with all changes persisting across sessions. This creates a flywheel where the agent gets better at tasks over time by enhancing its own workspace.

### Core Features

- 🚀 **Instant Sandboxes** - Spin up isolated environments in <100ms via Fly.io Machines
- 🔒 **Secure Isolation** - Firecracker microVM-based isolation (same tech as AWS Lambda)
- 📁 **Persistent Workspaces** - All changes survive sessions and improve over time
- 🤖 **Multi-Agent System** - Users can spawn multiple agents, each with allocated tokens
- 💬 **Agent Communication** - Agents can send emails, SMS, and make calls on user's behalf
- 📊 **Token Tracking** - Real-time usage monitoring per user, per agent, per task
- 🔧 **Self-Improving** - Agents can install packages and modify their own tooling

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DELTA PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Web UI     │    │   REST API   │    │  WebSocket   │                   │
│  │  (Dashboard) │    │   Gateway    │    │  (Terminal)  │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                            │
│         └───────────────────┼───────────────────┘                            │
│                             ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        CORE SERVICES                                 │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│  │  │    Auth     │  │   Token     │  │   Agent     │  │  Messaging  │ │    │
│  │  │   Service   │  │   Metering  │  │ Orchestrator│  │   Service   │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                             │                                                │
│                             ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      SANDBOX LAYER (Fly.io)                          │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │    │
│  │  │Agent VM │  │Agent VM │  │Agent VM │  │Agent VM │  │   ...   │   │    │
│  │  │(User A) │  │(User A) │  │(User B) │  │(User C) │  │         │   │    │
│  │  │ Agent 1 │  │ Agent 2 │  │ Agent 1 │  │ Agent 1 │  │         │   │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        DATA LAYER                                    │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│  │  │  PostgreSQL │  │    Redis    │  │ Cloudflare  │  │   Vector    │ │    │
│  │  │  (Users,    │  │  (Sessions, │  │     R2      │  │    DB       │ │    │
│  │  │   Agents)   │  │   Cache)    │  │  (Files)    │  │  (Memory)   │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EXTERNAL INTEGRATIONS                             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │    │
│  │  │   Stripe    │  │  AWS SES    │  │   Twilio    │  │   Claude    │ │    │
│  │  │ (Payments)  │  │  (Email)    │  │ (SMS/Calls) │  │  Agent SDK  │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Token & Agent System

### How Token Allocation Works

```
User Account (1000 tokens/month)
├── Main Agent (allocated: 500 tokens)
│   ├── Task: "Build data pipeline" (used: 120 tokens)
│   └── Task: "Debug API" (used: 45 tokens)
├── Bot Agent 1 - Email Bot (allocated: 100 tokens, limited permissions)
│   └── Task: "Send daily report" (used: 15 tokens)
├── Bot Agent 2 - SMS Bot (allocated: 50 tokens, limited permissions)
│   └── Task: "Send appointment reminder" (used: 8 tokens)
└── Reserve Pool (350 tokens - unallocated)

Token Transfer Flow:
Bot → requests tokens → Main Agent → approves → User Dashboard → confirms
```

### Agent Hierarchy

| Agent Type | Permissions | Token Access | Communication |
|------------|-------------|--------------|---------------|
| **Main Agent** | Full workspace access | Can allocate to bots | All channels |
| **Bot Agent** | Limited, task-specific | Must request from main | Single channel |
| **Messenger Bot** | Minimal, send-only | Fixed small allocation | Specific channel |

---

## 💬 Communication System

### Available Channels

| Channel | Provider | Cost per Unit | Rate Limits |
|---------|----------|---------------|-------------|
| **Email** | AWS SES | $0.10/1000 emails | 100/day (free tier) |
| **SMS** | Twilio | $0.0079/message | 50/day (free tier) |
| **Voice** | Twilio | $0.013/minute | 10 calls/day (free tier) |

### Security Model

- All messenger bots get **bare minimum information**
- Each bot has a **single task** and **limited scope**
- User must **pre-approve** message templates
- All communications are **logged and auditable**
- Main phone/email owned by DELTA, not exposed to bots

---

## 🚀 Quick Start

### Option A: Local Development with Docker

```bash
# Build and run locally (uses port 8000 by default)
./scripts/docker-local.sh

# Or specify a custom port
./scripts/docker-local.sh 8080

# Test the health endpoint
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Run Docker integration tests
pytest tests/v0.1/test_docker.py -v

# View container logs
docker logs -f delta-local

# Stop the container
docker stop delta-local
```

### Option B: Deploy to Cloud (Railway/Render)

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

```bash
# Push to main branch - Railway/Render auto-deploys
git push origin main

# Environment variables are configured in the platform dashboard
# PORT is injected automatically at runtime
```

**Quick Test After Deployment:**
```bash
# Replace with your actual deployment URL
curl https://your-app.railway.app/health
curl https://your-app.railway.app/docs
```

### Installation (SDK)

```bash
# Python SDK
pip install delta-agents

# TypeScript SDK
npm install @delta-agents/sdk
```

### Basic Usage

```python
import asyncio
from delta import Delta, AgentConfig

async def main():
    # Initialize with your API key
    async with Delta(api_key="your-api-key") as client:
        
        # Create a main agent
        agent = await client.agents.create(
            name="dev-agent",
            config=AgentConfig(
                template="python-3.12",
                memory_mb=2048,
                token_budget=500
            )
        )
        
        # Execute commands in the sandbox
        result = await agent.exec("pip install pandas numpy")
        print(result.stdout)
        
        # Agent can self-improve
        await agent.files.write("/workspace/tools/analyze.py", """
import pandas as pd
def analyze(data):
    return pd.DataFrame(data).describe()
""")
        
        # Create a messenger bot with limited permissions
        email_bot = await client.agents.create_bot(
            parent_agent=agent,
            type="email",
            task="Send daily status reports",
            token_budget=50
        )
        
        # Bot requests to send email (requires pre-approval)
        await email_bot.send_message(
            template="daily_report",
            recipient="team@company.com",
            data={"status": "All systems operational"}
        )

asyncio.run(main())
```

---

## 📁 Project Structure

```
uva/
├── README.md                 # This file
├── pyproject.toml           # Python dependencies
├── Dockerfile               # Production container
├── Procfile                 # Heroku/Railway/Render process file
├── railway.json             # Railway deployment config
├── render.yaml              # Render.com deployment config
├── env.example              # Environment variables template
├── DEPLOY.md                # Deployment guide
├── SETUP_GUIDE.md           # Setup instructions
├── LICENSE                  # MIT License
│
├── src/
│   └── delta/               # Core Python package
│       ├── __init__.py
│       ├── config.py        # Configuration management
│       │
│       ├── api/             # FastAPI REST endpoints
│       │   ├── __init__.py
│       │   ├── main.py      # Application entry point
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py
│       │   │   ├── agents.py
│       │   │   ├── sandboxes.py
│       │   │   ├── files.py
│       │   │   ├── exec.py
│       │   │   └── messaging.py
│       │   └── websocket/   # WebSocket handlers
│       │       ├── __init__.py
│       │       └── terminal.py
│       │
│       ├── core/            # Core business logic
│       │   ├── __init__.py
│       │   ├── auth.py      # Authentication & accounts
│       │   ├── tokens.py    # Token metering & allocation
│       │   ├── agents.py    # Agent lifecycle management
│       │   └── messaging.py # Email/SMS/Voice handling
│       │
│       ├── sdk/             # Python SDK client
│       │   ├── __init__.py
│       │   ├── client.py
│       │   └── models.py
│       │
│       └── models/          # Database models
│           ├── __init__.py
│           ├── user.py
│           ├── agent.py
│           ├── token_usage.py
│           └── message_log.py
│
├── tests/                   # Test suites
│   ├── __init__.py
│   └── v0.1/               # Version 0.1 tests
│       ├── __init__.py
│       ├── README.md        # Test documentation
│       ├── test_auth.py
│       ├── test_agents.py
│       ├── test_sandbox.py
│       ├── test_tokens.py
│       ├── test_messaging.py
│       └── test_docker.py   # Docker integration tests
│
├── scripts/                 # Utility scripts
│   ├── start.sh            # Container startup script
│   └── docker-local.sh     # Local Docker dev script
│
├── docs/                    # Documentation
│   └── ARCHITECTURE.md      # Detailed architecture
│
└── examples/                # Example usage
    └── agent_client.py      # Agent WebSocket client example
```

---

## 🐳 Docker & Deployment

### Deployment Options

DELTA supports multiple deployment targets. Choose based on your needs:

| Platform | Best For | Pricing | Setup Difficulty |
|----------|----------|---------|------------------|
| **Railway** | Production (recommended) | Free tier + pay-as-you-go | Easy |
| **Render** | Production alternative | Free tier available | Easy |
| **Local Docker** | Development & testing | Free | Easy |

### Quick Comparison: Local Docker vs Cloud

| Aspect | Local Docker | Railway/Render (Production) |
|--------|--------------|----------------------------|
| Port | Set via `-e PORT=8000` or defaults to 8000 | Injected automatically by platform |
| Database | SQLite (default) | PostgreSQL (via `DATABASE_URL`) |
| Redis | Optional | Configured via `REDIS_URL` |
| Debug | Enabled (`-e DEBUG=true`) | Disabled |
| CORS | Allow all | Configure for production |
| Health Check | `http://localhost:8000/health` | Auto-configured by platform |

---

### Option 1: Railway (Recommended for Production)

Railway auto-deploys from GitHub and handles PORT injection automatically.

**Configuration Files:**
- `railway.json` - Build and deploy settings
- `Dockerfile` - Container definition
- `scripts/start.sh` - Startup script (handles PORT env var)

**Deploy Steps:**
1. Sign up at https://railway.app (use GitHub login)
2. Create new project → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables:
   ```bash
   SECRET_KEY=<generate-random-32-char-string>
   JWT_SECRET_KEY=<generate-random-32-char-string>
   DATABASE_URL=sqlite+aiosqlite:///./delta.db  # Or PostgreSQL URL
   ENVIRONMENT=production
   DEBUG=false
   ```
5. Deploy! Railway auto-detects the Dockerfile

**How Railway Works:**
- Railway injects `PORT` environment variable at runtime
- `scripts/start.sh` reads `PORT` and starts uvicorn on that port
- Health checks hit `/health` endpoint (configured in `railway.json`)

---

### Option 2: Render.com

**Configuration File:** `render.yaml`

**Deploy Steps:**
1. Sign up at https://render.com (use GitHub login)
2. New → Web Service → Connect GitHub repo
3. Settings: Runtime: Docker, Instance Type: Free
4. Environment variables same as Railway
5. Create Web Service

---

### Option 3: Local Docker (Development)

For local development and testing without cloud deployment.

```bash
# Build and run locally (uses port 8000 by default)
./scripts/docker-local.sh

# Or specify a custom port
./scripts/docker-local.sh 8080

# Test the health endpoint
curl http://localhost:8000/health

# View container logs
docker logs -f delta-local

# Stop the container
docker stop delta-local
```

**What the script does:**
1. Builds Docker image from `Dockerfile`
2. Runs container with `-e PORT=8000 -e DEBUG=true`
3. Maps port to host
4. Runs health check to verify startup

---

### Environment Variables Reference

```bash
# Required for production
SECRET_KEY=your-secret-key         # Set manually (32+ chars)
JWT_SECRET_KEY=your-jwt-secret     # Set manually (32+ chars)

# Database (optional - defaults to SQLite)
DATABASE_URL=postgresql://...      # Set by Railway/Render or manually
REDIS_URL=redis://...              # Optional caching

# Optional integrations
FLY_API_TOKEN=...                  # For Fly.io sandbox VMs
ANTHROPIC_API_KEY=...              # For Claude AI
STRIPE_SECRET_KEY=...              # For payments
```

See `env.example` for full list of environment variables.

---

### Dockerfile Architecture

The container uses a startup script (`scripts/start.sh`) to properly handle the `PORT` environment variable:

```bash
#!/bin/bash
PORT="${PORT:-8000}"
echo "Starting DELTA Platform on port $PORT"
exec uvicorn delta.api.main:app --host 0.0.0.0 --port "$PORT"
```

This ensures compatibility with:
- **Railway**: Injects PORT at runtime
- **Render**: Injects PORT at runtime  
- **Local Docker**: Uses PORT=8000 default or custom `-e PORT=XXXX`
- **Procfile**: For Heroku-style deployments

---

## 🔧 Infrastructure

### Cloud Provider: Fly.io (Primary)

**Why Fly.io?**
- Uses Firecracker microVMs (same as AWS Lambda)
- Data centers in **San Jose, CA** (sjc) - perfect for Bay Area
- Pay-per-second billing: ~$0.0000008/second
- Fast boot times (<300ms)
- No self-hosting required

### Cost Estimates

| Usage Tier | Agents | Est. Monthly Cost |
|------------|--------|-------------------|
| **Free** | 1 agent, 10 hrs/mo | $0 (trial credits) |
| **Developer** | 3 agents, 100 hrs/mo | ~$15-25 |
| **Pro** | 10 agents, 500 hrs/mo | ~$50-100 |
| **Enterprise** | Unlimited | Custom |

### Additional Services

| Service | Provider | Monthly Cost |
|---------|----------|--------------|
| Database | Neon PostgreSQL | $0-19 |
| Cache | Upstash Redis | $0-10 |
| Storage | Cloudflare R2 | ~$0.015/GB |
| Email | AWS SES | ~$0.10/1000 |
| SMS | Twilio | Pay-per-use |

---

## 🔐 Security

### Authentication Flow

1. **User Registration** → Email verification → Password (Argon2id hash)
2. **API Keys** → Scoped per agent, rotatable, revocable
3. **Agent Auth** → JWT tokens with limited TTL
4. **Bot Auth** → Restricted tokens, task-specific permissions

### Isolation Model

```
┌─────────────────────────────────────────┐
│           Firecracker microVM           │
│  ┌───────────────────────────────────┐  │
│  │     Agent Workspace (sandboxed)   │  │
│  │  - Isolated filesystem            │  │
│  │  - Limited network (egress only)  │  │
│  │  - CPU/memory limits              │  │
│  │  - No access to host              │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 📈 Roadmap

### v0.1 (Current) - Foundation
- [x] Project structure
- [ ] User authentication
- [ ] Basic sandbox (Fly.io integration)
- [ ] Token metering
- [ ] Email messaging
- [ ] Test suite

### v0.2 - Agent System
- [ ] Multi-agent support
- [ ] Bot agents with limited permissions
- [ ] SMS/Voice integration
- [ ] Agent memory persistence

### v0.3 - Self-Improvement
- [ ] Package installation tracking
- [ ] Skill persistence
- [ ] Rollback/snapshots
- [ ] Agent collaboration

### v1.0 - Production Ready
- [ ] Payment integration (Stripe)
- [ ] Team collaboration
- [ ] Dashboard UI
- [ ] Enterprise features

---

## 🧪 Running Tests

```bash
# Run all v0.1 tests (unit tests)
pytest tests/v0.1/ -v

# Run specific test
pytest tests/v0.1/test_auth.py -v

# Run with coverage
pytest tests/v0.1/ --cov=src/delta --cov-report=html

# Run Docker integration tests (requires running container)
./scripts/docker-local.sh 8000
pytest tests/v0.1/test_docker.py -v

# Quick connectivity check (without pytest)
python tests/v0.1/test_docker.py
```

### Test Categories

| Test File | Type | Requirements |
|-----------|------|--------------|
| `test_auth.py` | Unit | None |
| `test_agents.py` | Unit | None |
| `test_sandbox.py` | Unit | None |
| `test_tokens.py` | Unit | None |
| `test_messaging.py` | Unit | None |
| `test_docker.py` | Integration | Running Docker container |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Documentation**: [Google Doc](https://docs.google.com/document/d/1lGc8EZbQq5pW0jq3Lgl95sk9RQMQiHCXZjQMIdIdP98/edit?tab=t.0)
- **Issues**: [GitHub Issues](https://github.com/stickfigure3/DELTA/issues)

---

*Built with ❤️ for the future of AI agents*
