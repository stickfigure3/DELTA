"""Token metering tests for DELTA v0.1."""

import pytest
from uuid import uuid4
from datetime import datetime

from delta.core.tokens import TokenService, TokenTracker


class TestTokenService:
    """Test token metering service."""
    
    def test_calculate_llm_cost_basic(self):
        """Test basic LLM cost calculation."""
        service = TokenService()
        
        cost = service.calculate_llm_cost(
            prompt_tokens=1000,
            completion_tokens=500,
            model="claude-3-sonnet"
        )
        
        assert cost > 0
        assert isinstance(cost, int)
    
    def test_calculate_llm_cost_opus_more_expensive(self):
        """Test that Opus model costs more."""
        service = TokenService()
        
        sonnet_cost = service.calculate_llm_cost(1000, 500, "claude-3-sonnet")
        opus_cost = service.calculate_llm_cost(1000, 500, "claude-3-opus")
        
        assert opus_cost > sonnet_cost
    
    def test_calculate_llm_cost_haiku_cheaper(self):
        """Test that Haiku model costs less."""
        service = TokenService()
        
        sonnet_cost = service.calculate_llm_cost(1000, 500, "claude-3-sonnet")
        haiku_cost = service.calculate_llm_cost(1000, 500, "claude-3-haiku")
        
        assert haiku_cost < sonnet_cost
    
    def test_calculate_message_cost(self):
        """Test message cost calculation."""
        service = TokenService()
        
        email_cost = service.calculate_message_cost("email")
        sms_cost = service.calculate_message_cost("sms")
        call_cost = service.calculate_message_cost("voice_call")
        
        assert email_cost < sms_cost < call_cost
    
    def test_get_tier_limit(self):
        """Test tier limit retrieval."""
        service = TokenService()
        
        assert service.get_tier_limit("free") == 1000
        assert service.get_tier_limit("developer") == 10000
        assert service.get_tier_limit("pro") == 100000
        assert service.get_tier_limit("enterprise") == -1  # Unlimited
    
    def test_check_budget_allowed(self):
        """Test budget check when within limits."""
        service = TokenService()
        
        allowed, remaining = service.check_budget(
            allocated=100,
            used=50,
            requested=30
        )
        
        assert allowed is True
        assert remaining == 20
    
    def test_check_budget_denied(self):
        """Test budget check when exceeding limits."""
        service = TokenService()
        
        allowed, remaining = service.check_budget(
            allocated=100,
            used=90,
            requested=20
        )
        
        assert allowed is False
        assert remaining == 10


class TestTokenTracker:
    """Test token usage tracking."""
    
    def test_record_llm_usage(self):
        """Test recording LLM usage."""
        tracker = TokenTracker(uuid4(), "test-task")
        
        cost = tracker.record_llm_usage(1000, 500, "claude-3-sonnet")
        
        assert cost > 0
        assert tracker.get_total_cost() == cost
    
    def test_record_tool_usage(self):
        """Test recording tool usage."""
        tracker = TokenTracker(uuid4())
        
        cost = tracker.record_tool_usage("file_read")
        
        assert cost == 5  # TOOL_EXECUTION cost
    
    def test_record_message(self):
        """Test recording message sending."""
        tracker = TokenTracker(uuid4())
        
        email_cost = tracker.record_message("email")
        sms_cost = tracker.record_message("sms")
        
        assert email_cost == 10
        assert sms_cost == 20
    
    def test_get_summary(self):
        """Test getting usage summary."""
        tracker = TokenTracker(uuid4(), "test-task")
        
        tracker.record_llm_usage(1000, 500, "claude-3-sonnet")
        tracker.record_tool_usage("file_read")
        tracker.record_message("email")
        
        summary = tracker.get_summary()
        
        assert "total_cost" in summary
        assert "breakdown" in summary
        assert summary["task_id"] == "test-task"
        assert summary["operations"] == 3
    
    def test_multiple_operations(self):
        """Test tracking multiple operations."""
        tracker = TokenTracker(uuid4())
        
        tracker.record_llm_usage(500, 200, "claude-3-haiku")
        tracker.record_llm_usage(500, 200, "claude-3-haiku")
        tracker.record_tool_usage("exec")
        tracker.record_message("sms")
        
        summary = tracker.get_summary()
        
        assert summary["operations"] == 4
        assert summary["breakdown"]["messages"] == 20


class TestTokenReset:
    """Test token reset date calculation."""
    
    def test_calculate_reset_date(self):
        """Test reset date is in the future."""
        service = TokenService()
        
        reset_date = service.calculate_reset_date()
        
        assert reset_date > datetime.utcnow()
        assert reset_date.day == 1  # First of month
