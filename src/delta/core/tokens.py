"""Token metering and allocation service."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from delta.models.token_usage import TokenUsageType


class TokenService:
    """
    Handle token metering, allocation, and budget management.
    
    Token Flow:
    1. User has monthly token allocation based on tier
    2. User allocates tokens to agents
    3. Agents consume tokens for LLM calls, tool use, messaging
    4. Bots can request more tokens from main agent
    5. All usage is tracked and auditable
    """
    
    # Token costs for different operations
    COSTS = {
        TokenUsageType.LLM_PROMPT: 1,      # per 1000 tokens
        TokenUsageType.LLM_COMPLETION: 3,  # per 1000 tokens (more expensive)
        TokenUsageType.TOOL_EXECUTION: 5,  # per execution
        TokenUsageType.FILE_OPERATION: 1,  # per operation
        TokenUsageType.MESSAGE_SEND: 10,   # per message (email/sms)
    }
    
    # Tier limits
    TIER_LIMITS = {
        "free": 1000,
        "developer": 10000,
        "pro": 100000,
        "enterprise": -1,  # Unlimited
    }
    
    def calculate_llm_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "claude-3-sonnet",
    ) -> int:
        """Calculate token cost for an LLM call."""
        # Adjust for model (more expensive models cost more)
        model_multiplier = {
            "claude-3-opus": 3.0,
            "claude-3-sonnet": 1.0,
            "claude-3-haiku": 0.5,
        }.get(model, 1.0)
        
        prompt_cost = (prompt_tokens / 1000) * self.COSTS[TokenUsageType.LLM_PROMPT]
        completion_cost = (completion_tokens / 1000) * self.COSTS[TokenUsageType.LLM_COMPLETION]
        
        return int((prompt_cost + completion_cost) * model_multiplier)
    
    def calculate_message_cost(self, message_type: str) -> int:
        """Calculate token cost for sending a message."""
        costs = {
            "email": 10,
            "sms": 20,
            "voice_call": 50,
        }
        return costs.get(message_type, 10)
    
    def get_tier_limit(self, tier: str) -> int:
        """Get the monthly token limit for a tier."""
        return self.TIER_LIMITS.get(tier, 1000)
    
    def check_budget(
        self,
        allocated: int,
        used: int,
        requested: int,
    ) -> tuple[bool, int]:
        """
        Check if an operation fits within budget.
        
        Returns:
            (allowed, remaining) - whether operation is allowed and remaining tokens
        """
        remaining = allocated - used
        if requested > remaining:
            return False, remaining
        return True, remaining - requested
    
    def calculate_reset_date(self, current_reset: Optional[datetime] = None) -> datetime:
        """Calculate the next token reset date (monthly)."""
        now = datetime.utcnow()
        if current_reset and current_reset > now:
            return current_reset
        
        # Reset on the 1st of next month
        if now.month == 12:
            return datetime(now.year + 1, 1, 1)
        return datetime(now.year, now.month + 1, 1)


class TokenTracker:
    """
    Track token usage for a specific session/task.
    
    Usage:
        tracker = TokenTracker(agent_id, task_id)
        tracker.record_llm_usage(100, 50, "claude-3-sonnet")
        tracker.record_message("email")
        summary = tracker.get_summary()
    """
    
    def __init__(self, agent_id: UUID, task_id: Optional[str] = None):
        self.agent_id = agent_id
        self.task_id = task_id
        self.service = TokenService()
        self.usage: list[dict] = []
    
    def record_llm_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "claude-3-sonnet",
    ) -> int:
        """Record LLM token usage. Returns cost."""
        cost = self.service.calculate_llm_cost(prompt_tokens, completion_tokens, model)
        self.usage.append({
            "type": "llm",
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "model": model,
            "cost": cost,
            "timestamp": datetime.utcnow(),
        })
        return cost
    
    def record_tool_usage(self, tool_name: str) -> int:
        """Record tool execution. Returns cost."""
        cost = TokenService.COSTS[TokenUsageType.TOOL_EXECUTION]
        self.usage.append({
            "type": "tool",
            "tool_name": tool_name,
            "cost": cost,
            "timestamp": datetime.utcnow(),
        })
        return cost
    
    def record_message(self, message_type: str) -> int:
        """Record message sending. Returns cost."""
        cost = self.service.calculate_message_cost(message_type)
        self.usage.append({
            "type": "message",
            "message_type": message_type,
            "cost": cost,
            "timestamp": datetime.utcnow(),
        })
        return cost
    
    def get_total_cost(self) -> int:
        """Get total token cost for this session."""
        return sum(u["cost"] for u in self.usage)
    
    def get_summary(self) -> dict:
        """Get usage summary."""
        return {
            "agent_id": str(self.agent_id),
            "task_id": self.task_id,
            "total_cost": self.get_total_cost(),
            "breakdown": {
                "llm": sum(u["cost"] for u in self.usage if u["type"] == "llm"),
                "tools": sum(u["cost"] for u in self.usage if u["type"] == "tool"),
                "messages": sum(u["cost"] for u in self.usage if u["type"] == "message"),
            },
            "operations": len(self.usage),
        }
