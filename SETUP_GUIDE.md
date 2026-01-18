# DELTA Setup Guide for Team

## Quick Start for Developers

This guide will help you get DELTA running locally and deployed to Fly.io.

---

## Prerequisites

- macOS with Homebrew
- Python 3.12+ 
- Git access to this repo

---

## 1. Clone and Install Dependencies

```bash
# Clone the repo
git clone git@github.com:stickfigure3/DELTA.git
cd DELTA

# Install Python 3.12 if needed
brew install python@3.12

# Install Poetry (Python package manager)
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to your ~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# Set Python version and install dependencies
poetry env use $(brew --prefix python@3.12)/bin/python3.12
poetry install
```

---

## 2. Create Local Environment File

```bash
# Copy the example env file
cp env.example .env

# Edit .env and add these minimum values for local dev:
# SECRET_KEY=<any-32-char-string>
# JWT_SECRET_KEY=<any-32-char-string>
# DATABASE_URL=postgresql+asyncpg://localhost:5432/delta_dev
# REDIS_URL=redis://localhost:6379
```

---

## 3. Run Tests (Verify Everything Works)

```bash
poetry run pytest tests/v0.1/ -v
```

Expected: **56 passed, 7 skipped**

---

## 4. Set Up External Services

### A. Fly.io (Sandbox Infrastructure) - NEEDS EID VERIFICATION

```bash
# Install Fly CLI
brew install flyctl

# Login (requires EID/credit card for verification)
flyctl auth login

# After login, create the app
cd /path/to/DELTA
flyctl launch --name delta-api --region sjc --no-deploy

# Set secrets
flyctl secrets set SECRET_KEY="<generate-32-char-string>"
flyctl secrets set JWT_SECRET_KEY="<generate-32-char-string>"
flyctl secrets set DATABASE_URL="<neon-connection-string>"
flyctl secrets set REDIS_URL="<upstash-redis-url>"

# Deploy
flyctl deploy
```

### B. Neon PostgreSQL (Free Database)

1. Go to https://neon.tech
2. Sign up (free, no card required)
3. Create a new project called "delta"
4. Copy the connection string
5. Add to `.env`: `DATABASE_URL=<connection-string>`

### C. Upstash Redis (Free Cache)

1. Go to https://upstash.com
2. Sign up (free, no card required)
3. Create a Redis database
4. Copy the Redis URL
5. Add to `.env`: `REDIS_URL=<redis-url>`

---

## 5. Run the API Locally

```bash
poetry run uvicorn delta.api.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs for API documentation

---

## Project Structure

```
DELTA/
├── src/delta/           # Main Python package
│   ├── api/             # FastAPI endpoints
│   ├── core/            # Business logic (auth, tokens, agents, messaging)
│   ├── models/          # Database models
│   └── sdk/             # Python SDK client
├── tests/v0.1/          # Test suite
├── docs/                # Architecture diagrams
└── README.md            # Full documentation
```

---

## Key Features Already Built

✅ User authentication (Argon2id + JWT)  
✅ Token metering & budget allocation  
✅ Multi-agent hierarchy (Main Agent → Bots → Messengers)  
✅ Messaging service (Email/SMS/Voice) - needs Twilio/SES credentials  
✅ Python SDK client  
✅ 56 passing tests  

---

## What Needs To Be Done

1. **Fly.io Deployment** - Requires EID verification
2. **Neon Database Setup** - Free, no verification needed
3. **Upstash Redis Setup** - Free, no verification needed
4. **Twilio Account** (optional) - For SMS/Voice
5. **AWS SES** (optional) - For email sending

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | 32+ char secret for app |
| `JWT_SECRET_KEY` | Yes | 32+ char secret for JWT |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `FLY_API_TOKEN` | For deploy | Fly.io API token |
| `ANTHROPIC_API_KEY` | For LLM | Claude API key |
| `TWILIO_ACCOUNT_SID` | For SMS | Twilio credentials |
| `TWILIO_AUTH_TOKEN` | For SMS | Twilio credentials |
| `AWS_ACCESS_KEY_ID` | For email | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | For email | AWS credentials |

---

## Links

- **GitHub**: https://github.com/stickfigure3/DELTA
- **Google Doc**: https://docs.google.com/document/d/1lGc8EZbQq5pW0jq3Lgl95sk9RQMQiHCXZjQMIdIdP98/edit

---

## Questions?

Check the `docs/ARCHITECTURE.md` for detailed system diagrams or reach out in the group chat.
