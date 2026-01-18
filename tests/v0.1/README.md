# DELTA v0.1 Test Suite

This folder contains tests for DELTA v0.1 - the foundation release.

## Test Categories

### 1. Authentication Tests (`test_auth.py`)
- User registration
- Login/logout
- JWT token generation and verification
- Password hashing (Argon2id)
- API key generation

### 2. Agent Tests (`test_agents.py`)
- Agent creation (main agents)
- Bot creation (limited agents)
- Agent lifecycle (pause/resume/destroy)
- Permission system

### 3. Token Tests (`test_tokens.py`)
- Token metering
- Budget allocation
- Usage tracking
- Rate limiting

### 4. Messaging Tests (`test_messaging.py`)
- Email sending
- SMS sending
- Voice calls
- Message templates
- Rate limits per channel

### 5. Sandbox Tests (`test_sandbox.py`)
- Sandbox creation
- Command execution
- File operations
- Persistence

## Running Tests

```bash
# Run all v0.1 tests
pytest tests/v0.1/ -v

# Run specific test file
pytest tests/v0.1/test_auth.py -v

# Run with coverage
pytest tests/v0.1/ --cov=src/delta --cov-report=html

# Run only fast tests
pytest tests/v0.1/ -v -m "not slow"
```

## Test Status

| Test File | Status | Coverage |
|-----------|--------|----------|
| test_auth.py | 🟡 Scaffolded | - |
| test_agents.py | 🟡 Scaffolded | - |
| test_tokens.py | 🟡 Scaffolded | - |
| test_messaging.py | 🟡 Scaffolded | - |
| test_sandbox.py | 🟡 Scaffolded | - |

## v0.1 Checklist

- [x] Project structure created
- [x] Database models defined
- [x] API routes scaffolded
- [x] SDK client implemented
- [x] Authentication service
- [x] Token metering service
- [x] Messaging service
- [ ] Fly.io integration
- [ ] AWS SES integration
- [ ] Twilio integration
- [ ] End-to-end tests passing

## Notes

This test suite corresponds to the Google Doc state:
https://docs.google.com/document/d/1lGc8EZbQq5pW0jq3Lgl95sk9RQMQiHCXZjQMIdIdP98/edit
