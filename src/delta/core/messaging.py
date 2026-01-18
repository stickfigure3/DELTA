"""Messaging service for agent-to-user communication."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from delta.models.message_log import MessageStatus, MessageType


class MessagingService:
    """
    Handle all agent-to-user communication: email, SMS, voice calls.
    
    Security Model:
    - Bots have MINIMAL information and permissions
    - All messages must use pre-approved templates OR be approved by user
    - Rate limits per agent per day
    - All communications are logged and auditable
    - Main phone/email owned by DELTA, not exposed directly to bots
    """
    
    # Rate limits per agent per day
    RATE_LIMITS = {
        MessageType.EMAIL: 100,
        MessageType.SMS: 50,
        MessageType.VOICE_CALL: 10,
    }
    
    # Costs (in tokens)
    MESSAGE_COSTS = {
        MessageType.EMAIL: 10,
        MessageType.SMS: 20,
        MessageType.VOICE_CALL: 50,
    }
    
    def __init__(self):
        # These will be initialized with actual clients
        self.ses_client = None  # AWS SES
        self.twilio_client = None  # Twilio
    
    async def send_email(
        self,
        agent_id: UUID,
        user_id: UUID,
        recipient: str,
        subject: str,
        content: str,
        template_id: Optional[str] = None,
    ) -> dict:
        """
        Send an email on behalf of an agent.
        
        Returns message log entry.
        """
        message_id = uuid4()
        
        # TODO: Implement actual AWS SES sending
        # response = await self.ses_client.send_email(...)
        
        return {
            "id": message_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "message_type": MessageType.EMAIL,
            "status": MessageStatus.SENT,
            "recipient": recipient,
            "subject": subject,
            "content": content,
            "template_id": template_id,
            "tokens_used": self.MESSAGE_COSTS[MessageType.EMAIL],
            "created_at": datetime.utcnow(),
            "sent_at": datetime.utcnow(),
        }
    
    async def send_sms(
        self,
        agent_id: UUID,
        user_id: UUID,
        recipient: str,
        content: str,
        template_id: Optional[str] = None,
    ) -> dict:
        """
        Send an SMS on behalf of an agent.
        
        Uses Twilio with the main DELTA phone number.
        """
        message_id = uuid4()
        
        # TODO: Implement actual Twilio SMS sending
        # response = await self.twilio_client.messages.create(...)
        
        return {
            "id": message_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "message_type": MessageType.SMS,
            "status": MessageStatus.SENT,
            "recipient": recipient,
            "content": content,
            "template_id": template_id,
            "tokens_used": self.MESSAGE_COSTS[MessageType.SMS],
            "created_at": datetime.utcnow(),
            "sent_at": datetime.utcnow(),
        }
    
    async def make_call(
        self,
        agent_id: UUID,
        user_id: UUID,
        recipient: str,
        message: str,
        template_id: Optional[str] = None,
    ) -> dict:
        """
        Make a voice call on behalf of an agent.
        
        Uses Twilio with text-to-speech for the message.
        """
        message_id = uuid4()
        
        # TODO: Implement actual Twilio voice call
        # response = await self.twilio_client.calls.create(...)
        
        return {
            "id": message_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "message_type": MessageType.VOICE_CALL,
            "status": MessageStatus.SENT,
            "recipient": recipient,
            "content": message,
            "template_id": template_id,
            "tokens_used": self.MESSAGE_COSTS[MessageType.VOICE_CALL],
            "created_at": datetime.utcnow(),
            "sent_at": datetime.utcnow(),
        }
    
    async def send_internal_message(
        self,
        from_agent_id: UUID,
        to_agent_id: UUID,
        content: str,
        message_type: str = "token_request",
    ) -> dict:
        """
        Send an internal message between agents.
        
        Used for:
        - Bot requesting tokens from main agent
        - Status updates
        - Error notifications
        """
        message_id = uuid4()
        
        return {
            "id": message_id,
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "message_type": message_type,
            "content": content,
            "status": "delivered",
            "created_at": datetime.utcnow(),
        }
    
    def check_rate_limit(
        self,
        message_type: MessageType,
        messages_sent_today: int,
        agent_limit: Optional[int] = None,
    ) -> tuple[bool, int]:
        """
        Check if agent is within rate limits.
        
        Returns: (allowed, remaining)
        """
        limit = agent_limit or self.RATE_LIMITS[message_type]
        remaining = limit - messages_sent_today
        return remaining > 0, max(0, remaining)
    
    def get_message_cost(self, message_type: MessageType) -> int:
        """Get the token cost for a message type."""
        return self.MESSAGE_COSTS.get(message_type, 10)
    
    async def validate_template(
        self,
        template_id: str,
        variables: dict,
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a message against its template.
        
        Returns: (valid, error_message)
        """
        # TODO: Implement template validation
        return True, None
    
    async def render_template(
        self,
        template_id: str,
        variables: dict,
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Render a template with variables.
        
        Returns: (subject, content) or (None, None) if template not found
        """
        # TODO: Implement template rendering
        return None, None


class BotMessenger:
    """
    Restricted messenger for bot agents.
    
    Bots can ONLY:
    - Send messages using pre-approved templates
    - Send to pre-approved recipients
    - Within their rate limits
    - Using their allocated tokens
    """
    
    def __init__(
        self,
        bot_id: UUID,
        user_id: UUID,
        allowed_channels: list[str],
        max_messages_per_day: int,
        approved_templates: list[str],
        approved_recipients: Optional[list[str]] = None,
    ):
        self.bot_id = bot_id
        self.user_id = user_id
        self.allowed_channels = allowed_channels
        self.max_messages_per_day = max_messages_per_day
        self.approved_templates = approved_templates
        self.approved_recipients = approved_recipients
        self.service = MessagingService()
        self.messages_sent_today = 0
    
    def can_send(self, channel: str, recipient: str, template_id: str) -> tuple[bool, str]:
        """Check if bot can send this message."""
        if channel not in self.allowed_channels:
            return False, f"Channel '{channel}' not allowed for this bot"
        
        if template_id not in self.approved_templates:
            return False, f"Template '{template_id}' not approved for this bot"
        
        if self.approved_recipients and recipient not in self.approved_recipients:
            return False, f"Recipient '{recipient}' not in approved list"
        
        if self.messages_sent_today >= self.max_messages_per_day:
            return False, f"Daily message limit ({self.max_messages_per_day}) reached"
        
        return True, "OK"
    
    async def send(
        self,
        channel: str,
        recipient: str,
        template_id: str,
        variables: dict,
    ) -> dict:
        """Send a message if allowed."""
        can_send, reason = self.can_send(channel, recipient, template_id)
        if not can_send:
            return {"error": reason, "status": "rejected"}
        
        # Render template
        subject, content = await self.service.render_template(template_id, variables)
        if content is None:
            return {"error": "Template not found", "status": "rejected"}
        
        # Send based on channel
        if channel == "email":
            result = await self.service.send_email(
                self.bot_id, self.user_id, recipient, subject or "", content, template_id
            )
        elif channel == "sms":
            result = await self.service.send_sms(
                self.bot_id, self.user_id, recipient, content, template_id
            )
        elif channel == "voice_call":
            result = await self.service.make_call(
                self.bot_id, self.user_id, recipient, content, template_id
            )
        else:
            return {"error": f"Unknown channel: {channel}", "status": "rejected"}
        
        self.messages_sent_today += 1
        return result
