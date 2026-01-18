# DELTA Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 DELTA PLATFORM                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                            CLIENT LAYER                                  │    │
│  │                                                                          │    │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐               │    │
│  │   │  Python SDK  │   │    TS SDK    │   │   REST API   │               │    │
│  │   │              │   │              │   │   Clients    │               │    │
│  │   └──────────────┘   └──────────────┘   └──────────────┘               │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                            API GATEWAY                                   │    │
│  │                                                                          │    │
│  │   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐               │    │
│  │   │    FastAPI   │   │   WebSocket  │   │    Auth      │               │    │
│  │   │   REST API   │   │   Terminal   │   │  Middleware  │               │    │
│  │   └──────────────┘   └──────────────┘   └──────────────┘               │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                          CORE SERVICES                                   │    │
│  │                                                                          │    │
│  │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │    │
│  │   │    Auth    │  │   Token    │  │   Agent    │  │ Messaging  │       │    │
│  │   │  Service   │  │  Metering  │  │ Orchestrator│  │  Service   │       │    │
│  │   │            │  │            │  │            │  │            │       │    │
│  │   │ • Register │  │ • Track    │  │ • Create   │  │ • Email    │       │    │
│  │   │ • Login    │  │ • Allocate │  │ • Pause    │  │ • SMS      │       │    │
│  │   │ • JWT      │  │ • Budget   │  │ • Resume   │  │ • Calls    │       │    │
│  │   │ • API Keys │  │ • Limits   │  │ • Destroy  │  │ • Templates│       │    │
│  │   └────────────┘  └────────────┘  └────────────┘  └────────────┘       │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                         SANDBOX LAYER (Fly.io)                           │    │
│  │                                                                          │    │
│  │   ┌─────────────────────────────────────────────────────────────────┐   │    │
│  │   │                    Fly.io Machines API                           │   │    │
│  │   │                                                                  │   │    │
│  │   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │   │    │
│  │   │  │ Agent   │  │ Agent   │  │ Agent   │  │   ...   │            │   │    │
│  │   │  │ microVM │  │ microVM │  │ microVM │  │         │            │   │    │
│  │   │  │         │  │         │  │         │  │         │            │   │    │
│  │   │  │ User A  │  │ User A  │  │ User B  │  │         │            │   │    │
│  │   │  │ Main    │  │ Bot 1   │  │ Main    │  │         │            │   │    │
│  │   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │   │    │
│  │   │                                                                  │   │    │
│  │   └─────────────────────────────────────────────────────────────────┘   │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                           DATA LAYER                                     │    │
│  │                                                                          │    │
│  │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │    │
│  │   │ PostgreSQL │  │   Redis    │  │Cloudflare  │  │  Vector DB │       │    │
│  │   │   (Neon)   │  │ (Upstash)  │  │    R2      │  │ (Optional) │       │    │
│  │   │            │  │            │  │            │  │            │       │    │
│  │   │ • Users    │  │ • Sessions │  │ • Files    │  │ • Agent    │       │    │
│  │   │ • Agents   │  │ • Cache    │  │ • Backups  │  │   Memory   │       │    │
│  │   │ • Tokens   │  │ • Rates    │  │ • Assets   │  │ • Search   │       │    │
│  │   │ • Messages │  │            │  │            │  │            │       │    │
│  │   └────────────┘  └────────────┘  └────────────┘  └────────────┘       │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                      │                                           │
│                                      ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                       EXTERNAL INTEGRATIONS                              │    │
│  │                                                                          │    │
│  │   ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐       │    │
│  │   │   Stripe   │  │  AWS SES   │  │   Twilio   │  │  Anthropic │       │    │
│  │   │            │  │            │  │            │  │            │       │    │
│  │   │ • Payments │  │ • Emails   │  │ • SMS      │  │ • Claude   │       │    │
│  │   │ • Billing  │  │            │  │ • Calls    │  │   API      │       │    │
│  │   └────────────┘  └────────────┘  └────────────┘  └────────────┘       │    │
│  │                                                                          │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Token & Agent Hierarchy

```
                            ┌─────────────────────┐
                            │    USER ACCOUNT     │
                            │                     │
                            │  Tier: Developer    │
                            │  Tokens: 10,000/mo  │
                            └──────────┬──────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
           ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
           │  MAIN AGENT   │  │  MAIN AGENT   │  │   RESERVE     │
           │   "dev-1"     │  │   "dev-2"     │  │    POOL       │
           │               │  │               │  │               │
           │ Budget: 3000  │  │ Budget: 2000  │  │  5000 tokens  │
           │ Used: 1200    │  │ Used: 500     │  │  (unallocated)│
           └───────┬───────┘  └───────────────┘  └───────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐
   │EMAIL BOT│ │ SMS BOT │ │TASK BOT │
   │         │ │         │ │         │
   │Budget:  │ │Budget:  │ │Budget:  │
   │  100    │ │   50    │ │  200    │
   │         │ │         │ │         │
   │Channels:│ │Channels:│ │Channels:│
   │ [email] │ │  [sms]  │ │ [none]  │
   └─────────┘ └─────────┘ └─────────┘


Token Request Flow:
─────────────────────────────────────────────────────────

  ┌─────────┐     1. Request      ┌─────────────┐
  │   BOT   │ ─────────────────▶  │ MAIN AGENT  │
  │         │                     │             │
  │ "Need   │     2. Forward      │  Review &   │
  │  more   │ ◀───────────────── │  Approve    │
  │ tokens" │                     │             │
  └─────────┘     3. Allocate     └──────┬──────┘
       ▲         ◀────────────────────────┘
       │
       │ OR
       │
       │         1. Direct Request
       │        ─────────────────────▶  ┌──────────────┐
       └────────────────────────────────│    USER      │
                2. Manual Approval      │  DASHBOARD   │
               ◀─────────────────────── │              │
                                        └──────────────┘
```

---

## Message Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         MESSAGE SECURITY MODEL                              │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   AGENT/BOT                    DELTA PLATFORM                  RECIPIENT   │
│                                                                             │
│  ┌─────────┐                  ┌─────────────┐                ┌──────────┐  │
│  │   Bot   │  1. Request      │  Messaging  │  4. Send       │  User's  │  │
│  │         │ ────────────────▶│   Service   │───────────────▶│  Email/  │  │
│  │ Limited │                  │             │                │  Phone   │  │
│  │  Info   │                  │ 2. Validate │                └──────────┘  │
│  └─────────┘                  │    - Template approved?                    │
│                               │    - Recipient allowed?                    │
│                               │    - Rate limit OK?                        │
│                               │    - Tokens available?                     │
│                               │                                            │
│                               │ 3. Transform                               │
│                               │    - Use DELTA's email/phone               │
│                               │    - Strip sensitive data                  │
│                               │    - Log for audit                         │
│                               └─────────────┘                              │
│                                                                             │
│  WHAT BOTS KNOW:              WHAT DELTA CONTROLS:                         │
│  ─────────────────            ─────────────────────                        │
│  • Template ID                • Actual email server                        │
│  • Variable values            • Phone number                               │
│  • Recipient (if allowed)     • Rate limiting                              │
│                               • Content filtering                          │
│  WHAT BOTS DON'T KNOW:        • Audit logging                              │
│  ─────────────────────                                                     │
│  • SMTP credentials                                                        │
│  • Twilio tokens                                                           │
│  • Full recipient list                                                     │
│  • Other users' data                                                       │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Models

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE SCHEMA                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐                    │
│  │        USERS        │         │       AGENTS        │                    │
│  ├─────────────────────┤         ├─────────────────────┤                    │
│  │ id (UUID, PK)       │◀────────│ user_id (FK)        │                    │
│  │ email               │    1:N  │ id (UUID, PK)       │                    │
│  │ password_hash       │         │ parent_agent_id (FK)│──┐ (self-ref)      │
│  │ name                │         │ name                │◀─┘                 │
│  │ status              │         │ agent_type          │                    │
│  │ tier                │         │ status              │                    │
│  │ total_tokens        │         │ fly_machine_id      │                    │
│  │ tokens_used         │         │ template            │                    │
│  │ stripe_customer_id  │         │ memory_mb           │                    │
│  │ created_at          │         │ token_budget        │                    │
│  └─────────────────────┘         │ tokens_used         │                    │
│                                  │ allowed_channels    │                    │
│                                  │ task_description    │                    │
│                                  │ created_at          │                    │
│  ┌─────────────────────┐         └─────────────────────┘                    │
│  │      API_KEYS       │                   │                                │
│  ├─────────────────────┤                   │                                │
│  │ id (UUID, PK)       │                   │                                │
│  │ user_id (FK)        │                   │ 1:N                            │
│  │ key_hash            │                   │                                │
│  │ key_prefix          │                   ▼                                │
│  │ name                │         ┌─────────────────────┐                    │
│  │ scopes              │         │    TOKEN_USAGE      │                    │
│  │ is_active           │         ├─────────────────────┤                    │
│  │ expires_at          │         │ id (UUID, PK)       │                    │
│  └─────────────────────┘         │ user_id (FK)        │                    │
│                                  │ agent_id (FK)       │                    │
│                                  │ usage_type          │                    │
│  ┌─────────────────────┐         │ tokens_used         │                    │
│  │   MESSAGE_LOGS      │         │ task_id             │                    │
│  ├─────────────────────┤         │ model               │                    │
│  │ id (UUID, PK)       │         │ created_at          │                    │
│  │ user_id (FK)        │         └─────────────────────┘                    │
│  │ agent_id (FK)       │                                                    │
│  │ message_type        │         ┌─────────────────────┐                    │
│  │ status              │         │ MESSAGE_TEMPLATES   │                    │
│  │ recipient           │         ├─────────────────────┤                    │
│  │ subject             │         │ id (UUID, PK)       │                    │
│  │ content             │         │ user_id (FK)        │                    │
│  │ template_id (FK)    │────────▶│ name                │                    │
│  │ external_id         │         │ message_type        │                    │
│  │ tokens_used         │         │ subject_template    │                    │
│  │ created_at          │         │ content_template    │                    │
│  │ sent_at             │         │ allowed_variables   │                    │
│  └─────────────────────┘         │ is_active           │                    │
│                                  └─────────────────────┘                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Infrastructure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          INFRASTRUCTURE DIAGRAM                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              ┌─────────────────┐                            │
│                              │   Cloudflare    │                            │
│                              │   (CDN + WAF)   │                            │
│                              └────────┬────────┘                            │
│                                       │                                      │
│                                       ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         FLY.IO (Primary)                             │    │
│  │                         Region: SJC (San Jose)                       │    │
│  │                                                                      │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                      API Server                              │   │    │
│  │   │                      (Fly Machine)                           │   │    │
│  │   │                                                              │   │    │
│  │   │   FastAPI + Uvicorn                                          │   │    │
│  │   │   2 vCPU / 1GB RAM                                           │   │    │
│  │   │   ~$5-10/month                                               │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                      │    │
│  │   ┌─────────────────────────────────────────────────────────────┐   │    │
│  │   │                    Agent Sandboxes                           │   │    │
│  │   │                    (Fly Machines)                            │   │    │
│  │   │                                                              │   │    │
│  │   │   ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐  │   │    │
│  │   │   │  Agent 1  │ │  Agent 2  │ │  Agent 3  │ │    ...    │  │   │    │
│  │   │   │  512MB    │ │  1GB      │ │  512MB    │ │           │  │   │    │
│  │   │   │  1 vCPU   │ │  2 vCPU   │ │  1 vCPU   │ │           │  │   │    │
│  │   │   └───────────┘ └───────────┘ └───────────┘ └───────────┘  │   │    │
│  │   │                                                              │   │    │
│  │   │   Cost: ~$0.0000008/second when running                     │   │    │
│  │   │         ~$2/month per always-on small agent                 │   │    │
│  │   └─────────────────────────────────────────────────────────────┘   │    │
│  │                                                                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                       │                                      │
│           ┌───────────────────────────┼───────────────────────────┐         │
│           │                           │                           │         │
│           ▼                           ▼                           ▼         │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐   │
│  │      Neon       │       │     Upstash     │       │  Cloudflare R2  │   │
│  │   PostgreSQL    │       │      Redis      │       │     Storage     │   │
│  │                 │       │                 │       │                 │   │
│  │  Free: 512MB    │       │  Free: 10K/day  │       │  $0.015/GB      │   │
│  │  Pro: $19/mo    │       │  Pro: $10/mo    │       │  Free egress    │   │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


Monthly Cost Estimate (Small Scale):
────────────────────────────────────
• API Server (Fly.io):     ~$10
• Agents (10 active):      ~$20-40
• Database (Neon):         $0-19
• Cache (Upstash):         $0-10
• Storage (R2):            ~$5
• Email (AWS SES):         ~$1
• SMS (Twilio):            Pay-per-use
────────────────────────────────────
TOTAL:                     ~$36-85/month
```

---

## Request Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API REQUEST FLOW                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   CLIENT                API GATEWAY              SERVICE                     │
│                                                                              │
│  ┌────────┐  1. POST /v1/agents           ┌────────────────┐                │
│  │ Python │  ──────────────────────────▶  │    FastAPI     │                │
│  │  SDK   │  Authorization: Bearer xxx    │    Router      │                │
│  └────────┘                               └───────┬────────┘                │
│                                                   │                          │
│                                           2. Validate JWT                    │
│                                                   │                          │
│                                                   ▼                          │
│                                           ┌────────────────┐                │
│                                           │  Auth Service  │                │
│                                           │                │                │
│                                           │  • Verify JWT  │                │
│                                           │  • Get User    │                │
│                                           │  • Check Tier  │                │
│                                           └───────┬────────┘                │
│                                                   │                          │
│                                           3. Check Token Budget              │
│                                                   │                          │
│                                                   ▼                          │
│                                           ┌────────────────┐                │
│                                           │ Token Service  │                │
│                                           │                │                │
│                                           │  • Get Budget  │                │
│                                           │  • Check Limit │                │
│                                           └───────┬────────┘                │
│                                                   │                          │
│                                           4. Create Agent VM                 │
│                                                   │                          │
│                                                   ▼                          │
│                                           ┌────────────────┐                │
│                                           │ Agent Service  │                │
│                                           │                │                │
│                                           │  • Fly.io API  │                │
│                                           │  • Create VM   │                │
│                                           │  • Save to DB  │                │
│                                           └───────┬────────┘                │
│                                                   │                          │
│  ┌────────┐  5. Response                         │                          │
│  │ Python │  ◀───────────────────────────────────┘                          │
│  │  SDK   │  { "id": "...", "status": "running" }                           │
│  └────────┘                                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Security Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SECURITY ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  LAYER 1: NETWORK                                                           │
│  ─────────────────                                                          │
│  • Cloudflare WAF (DDoS protection)                                         │
│  • HTTPS only (TLS 1.3)                                                     │
│  • Rate limiting at edge                                                    │
│                                                                              │
│  LAYER 2: AUTHENTICATION                                                    │
│  ────────────────────────                                                   │
│  • JWT tokens (short-lived, 30 min)                                         │
│  • Refresh tokens (7 days)                                                  │
│  • API keys (scoped, revocable)                                             │
│  • Argon2id password hashing                                                │
│                                                                              │
│  LAYER 3: AUTHORIZATION                                                     │
│  ───────────────────────                                                    │
│  • User → Agent ownership                                                   │
│  • Agent type permissions (MAIN/BOT/MESSENGER)                              │
│  • Token budget enforcement                                                 │
│  • Rate limits per agent                                                    │
│                                                                              │
│  LAYER 4: ISOLATION (Fly.io)                                                │
│  ───────────────────────────                                                │
│  • Firecracker microVM per agent                                            │
│  • Separate filesystem per agent                                            │
│  • Network isolation                                                        │
│  • Resource limits (CPU/RAM/Disk)                                           │
│                                                                              │
│  LAYER 5: DATA                                                              │
│  ─────────────                                                              │
│  • Encryption at rest (database)                                            │
│  • Encryption in transit (TLS)                                              │
│  • Per-user data isolation                                                  │
│  • Audit logging                                                            │
│                                                                              │
│  LAYER 6: MESSAGING                                                         │
│  ─────────────────                                                          │
│  • Template-based messaging only                                            │
│  • Pre-approved recipients                                                  │
│  • Rate limits per channel                                                  │
│  • Full audit trail                                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```
