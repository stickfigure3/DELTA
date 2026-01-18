"""Messaging tests for DELTA v0.1."""

import pytest
from uuid import uuid4

from delta.core.messaging import MessagingService, BotMessenger
from delta.models.message_log import MessageType, MessageStatus


class TestMessagingService:
    """Test messaging service."""
    
    @pytest.mark.asyncio
    async def test_send_email(self):
        """Test sending an email."""
        service = MessagingService()
        
        result = await service.send_email(
            agent_id=uuid4(),
            user_id=uuid4(),
            recipient="test@example.com",
            subject="Test Subject",
            content="Test content",
        )
        
        assert result["message_type"] == MessageType.EMAIL
        assert result["status"] == MessageStatus.SENT
        assert result["recipient"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_send_sms(self):
        """Test sending an SMS."""
        service = MessagingService()
        
        result = await service.send_sms(
            agent_id=uuid4(),
            user_id=uuid4(),
            recipient="+1234567890",
            content="Test SMS",
        )
        
        assert result["message_type"] == MessageType.SMS
        assert result["status"] == MessageStatus.SENT
    
    @pytest.mark.asyncio
    async def test_make_call(self):
        """Test making a voice call."""
        service = MessagingService()
        
        result = await service.make_call(
            agent_id=uuid4(),
            user_id=uuid4(),
            recipient="+1234567890",
            message="Hello, this is a test call.",
        )
        
        assert result["message_type"] == MessageType.VOICE_CALL
        assert result["status"] == MessageStatus.SENT


class TestMessageCosts:
    """Test message cost calculation."""
    
    def test_email_cost(self):
        """Test email costs tokens."""
        service = MessagingService()
        cost = service.get_message_cost(MessageType.EMAIL)
        assert cost == 10
    
    def test_sms_cost(self):
        """Test SMS costs more than email."""
        service = MessagingService()
        email_cost = service.get_message_cost(MessageType.EMAIL)
        sms_cost = service.get_message_cost(MessageType.SMS)
        assert sms_cost > email_cost
    
    def test_voice_call_cost(self):
        """Test voice call costs most."""
        service = MessagingService()
        sms_cost = service.get_message_cost(MessageType.SMS)
        call_cost = service.get_message_cost(MessageType.VOICE_CALL)
        assert call_cost > sms_cost


class TestRateLimits:
    """Test message rate limiting."""
    
    def test_check_rate_limit_allowed(self):
        """Test rate limit when under limit."""
        service = MessagingService()
        
        allowed, remaining = service.check_rate_limit(
            MessageType.EMAIL,
            messages_sent_today=50,
        )
        
        assert allowed is True
        assert remaining == 50
    
    def test_check_rate_limit_exceeded(self):
        """Test rate limit when exceeded."""
        service = MessagingService()
        
        allowed, remaining = service.check_rate_limit(
            MessageType.EMAIL,
            messages_sent_today=100,
        )
        
        assert allowed is False
        assert remaining == 0
    
    def test_custom_agent_limit(self):
        """Test custom rate limit per agent."""
        service = MessagingService()
        
        allowed, remaining = service.check_rate_limit(
            MessageType.SMS,
            messages_sent_today=5,
            agent_limit=10,
        )
        
        assert allowed is True
        assert remaining == 5


class TestBotMessenger:
    """Test restricted bot messenger."""
    
    def test_can_send_allowed_channel(self):
        """Test bot can send on allowed channel."""
        messenger = BotMessenger(
            bot_id=uuid4(),
            user_id=uuid4(),
            allowed_channels=["email"],
            max_messages_per_day=10,
            approved_templates=["daily_report"],
        )
        
        can_send, reason = messenger.can_send("email", "test@example.com", "daily_report")
        
        assert can_send is True
    
    def test_cannot_send_disallowed_channel(self):
        """Test bot cannot send on disallowed channel."""
        messenger = BotMessenger(
            bot_id=uuid4(),
            user_id=uuid4(),
            allowed_channels=["email"],
            max_messages_per_day=10,
            approved_templates=["daily_report"],
        )
        
        can_send, reason = messenger.can_send("sms", "+1234567890", "daily_report")
        
        assert can_send is False
        assert "not allowed" in reason
    
    def test_cannot_send_unapproved_template(self):
        """Test bot cannot use unapproved template."""
        messenger = BotMessenger(
            bot_id=uuid4(),
            user_id=uuid4(),
            allowed_channels=["email"],
            max_messages_per_day=10,
            approved_templates=["daily_report"],
        )
        
        can_send, reason = messenger.can_send("email", "test@example.com", "spam_template")
        
        assert can_send is False
        assert "not approved" in reason
    
    def test_rate_limit_enforcement(self):
        """Test bot respects daily rate limit."""
        messenger = BotMessenger(
            bot_id=uuid4(),
            user_id=uuid4(),
            allowed_channels=["email"],
            max_messages_per_day=2,
            approved_templates=["report"],
        )
        
        # Simulate sending max messages
        messenger.messages_sent_today = 2
        
        can_send, reason = messenger.can_send("email", "test@example.com", "report")
        
        assert can_send is False
        assert "limit" in reason.lower()
    
    def test_approved_recipients(self):
        """Test bot can only send to approved recipients."""
        messenger = BotMessenger(
            bot_id=uuid4(),
            user_id=uuid4(),
            allowed_channels=["email"],
            max_messages_per_day=10,
            approved_templates=["report"],
            approved_recipients=["allowed@example.com"],
        )
        
        can_send, _ = messenger.can_send("email", "allowed@example.com", "report")
        assert can_send is True
        
        can_send, reason = messenger.can_send("email", "notallowed@example.com", "report")
        assert can_send is False
        assert "not in approved" in reason


class TestInternalMessages:
    """Test internal agent-to-agent messaging."""
    
    @pytest.mark.asyncio
    async def test_send_internal_message(self):
        """Test sending internal message between agents."""
        service = MessagingService()
        
        result = await service.send_internal_message(
            from_agent_id=uuid4(),
            to_agent_id=uuid4(),
            content="Requesting 50 more tokens for task completion",
            message_type="token_request",
        )
        
        assert result["message_type"] == "token_request"
        assert result["status"] == "delivered"
