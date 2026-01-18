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

### Local Development with Docker

```bash
# Build and run locally (uses port 8000 by default)
./scripts/docker-local.sh

# Or specify a custom port
./scripts/docker-local.sh 8080

# Test the health endpoint
curl http://localhost:8000/health

# Run Docker tests
pytest tests/v0.1/test_docker.py -v

# View container logs
docker logs -f delta-local

# Stop the container
docker stop delta-local
```

### Deploy to Railway

```bash
# Push to main branch - Railway auto-deploys
git push origin main

# Environment variables are set automatically by Railway
# The PORT variable is injected at runtime
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
delta.2/
├── README.md                 # This file
├── pyproject.toml           # Python dependencies
├── package.json             # TypeScript SDK dependencies
│
├── src/
│   ├── delta/               # Core Python package
│   │   ├── __init__.py
│   │   ├── api/             # FastAPI REST endpoints
│   │   │   ├── main.py
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── agents.py
│   │   │   │   ├── sandboxes.py
│   │   │   │   ├── files.py
│   │   │   │   ├── exec.py
│   │   │   │   └── messaging.py
│   │   │   └── middleware/
│   │   │       ├── auth.py
│   │   │       └── rate_limit.py
│   │   │
│   │   ├── core/            # Core business logic
│   │   │   ├── auth.py      # Authentication & accounts
│   │   │   ├── tokens.py    # Token metering & allocation
│   │   │   ├── agents.py    # Agent lifecycle management
│   │   │   └── messaging.py # Email/SMS/Voice handling
│   │   │
│   │   ├── sandbox/         # Sandbox management
│   │   │   ├── flyio.py     # Fly.io Machines integration
│   │   │   ├── executor.py  # Command execution
│   │   │   └── filesystem.py# File operations
│   │   │
│   │   ├── sdk/             # Python SDK client
│   │   │   ├── client.py
│   │   │   └── models.py
│   │   │
│   │   ├── models/          # Database models
│   │   │   ├── user.py
│   │   │   ├── agent.py
│   │   │   ├── token_usage.py
│   │   │   └── message_log.py
│   │   │
│   │   └── config.py        # Configuration management
│   │
│   └── typescript/          # TypeScript SDK
│       ├── src/
│       │   ├── index.ts
│       │   ├── client.ts
│       │   └── types.ts
│       └── package.json
│
├── infra/                   # Infrastructure as Code
│   ├── terraform/           # Terraform configs
│   │   ├── main.tf
│   │   ├── flyio.tf
│   │   └── variables.tf
│   └── docker/
│       └── Dockerfile.sandbox
│
├── tests/                   # Test suites
│   └── v0.1/               # Version 0.1 tests
│       ├── test_auth.py
│       ├── test_agents.py
│       ├── test_sandbox.py
│       ├── test_tokens.py
│       ├── test_messaging.py
│       ├── test_docker.py   # Docker integration tests
│       └── README.md        # Test documentation
│
├── scripts/                 # Utility scripts
│   ├── start.sh            # Container startup script
│   └── docker-local.sh     # Local Docker dev script
│
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md      # Detailed architecture
│   ├── API.md              # API reference
│   └── diagrams/           # Visual diagrams
│       └── system_overview.mmd
│
└── examples/                # Example usage
    ├── basic_usage.py
    ├── multi_agent.py
    └── claude_integration.py
```

---

## 🐳 Docker & Deployment

### Local vs Production

| Aspect | Local Docker | Railway (Production) |
|--------|--------------|---------------------|
| Port | Set via `-e PORT=8000` or defaults to 8000 | Injected by Railway |
| Database | SQLite (default) | PostgreSQL (via `DATABASE_URL`) |
| Redis | Optional | Configured via `REDIS_URL` |
| Debug | Enabled | Disabled |
| CORS | Allow all | Configure for production |

### Environment Variables

```bash
# Required for production
DATABASE_URL=postgresql://...      # Set by Railway
REDIS_URL=redis://...              # Set by Railway  
SECRET_KEY=your-secret-key         # Set manually
JWT_SECRET_KEY=your-jwt-secret     # Set manually

# Optional integrations
FLY_API_TOKEN=...                  # For sandbox VMs
ANTHROPIC_API_KEY=...              # For Claude
STRIPE_SECRET_KEY=...              # For payments
```

### Dockerfile Architecture

The container uses a startup script (`scripts/start.sh`) to properly handle the `PORT` environment variable, which is required for Railway's health checks. The script:
1. Reads `PORT` from environment (defaults to 8000)
2. Starts uvicorn bound to `0.0.0.0:$PORT`
3. Logs startup information

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
