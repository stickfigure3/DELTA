"""Agent tests for DELTA v0.1."""

import pytest
from uuid import uuid4

from delta.core.agents import AgentService
from delta.models.agent import AgentConfig, AgentType, AgentStatus


class TestAgentCreation:
    """Test agent creation."""
    
    @pytest.mark.asyncio
    async def test_create_main_agent(self):
        """Test creating a main agent."""
        service = AgentService()
        user_id = uuid4()
        
        agent = await service.create_agent(
            user_id=user_id,
            name="test-agent",
            agent_type=AgentType.MAIN,
        )
        
        assert agent["name"] == "test-agent"
        assert agent["agent_type"] == AgentType.MAIN
        assert agent["status"] == AgentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_create_agent_with_config(self):
        """Test creating agent with custom config."""
        service = AgentService()
        user_id = uuid4()
        config = AgentConfig(
            template="python-3.11",
            memory_mb=1024,
            token_budget=500,
        )
        
        agent = await service.create_agent(
            user_id=user_id,
            name="custom-agent",
            config=config,
        )
        
        assert agent["template"] == "python-3.11"
        assert agent["memory_mb"] == 1024
        assert agent["token_budget"] == 500


class TestBotCreation:
    """Test bot agent creation."""
    
    @pytest.mark.asyncio
    async def test_create_bot(self):
        """Test creating a bot agent."""
        service = AgentService()
        user_id = uuid4()
        parent_id = uuid4()
        
        bot = await service.create_bot(
            user_id=user_id,
            parent_agent_id=parent_id,
            name="email-bot",
            task_description="Send daily status emails",
            allowed_channels=["email"],
            token_budget=50,
        )
        
        assert bot["name"] == "email-bot"
        assert bot["agent_type"] == AgentType.BOT
        assert bot["allowed_channels"] == ["email"]
        assert bot["token_budget"] == 50
    
    @pytest.mark.asyncio
    async def test_bot_has_parent(self):
        """Test that bots have parent agent reference."""
        service = AgentService()
        parent_id = uuid4()
        
        bot = await service.create_bot(
            user_id=uuid4(),
            parent_agent_id=parent_id,
            name="test-bot",
            task_description="Test task",
            allowed_channels=["sms"],
        )
        
        assert bot["parent_agent_id"] == parent_id


class TestAgentLifecycle:
    """Test agent lifecycle operations."""
    
    @pytest.mark.asyncio
    async def test_pause_agent(self):
        """Test pausing an agent."""
        service = AgentService()
        agent_id = uuid4()
        
        result = await service.pause_agent(agent_id)
        
        assert result["status"] == AgentStatus.PAUSED
    
    @pytest.mark.asyncio
    async def test_resume_agent(self):
        """Test resuming an agent."""
        service = AgentService()
        agent_id = uuid4()
        
        result = await service.resume_agent(agent_id)
        
        assert result["status"] == AgentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_destroy_agent(self):
        """Test destroying an agent."""
        service = AgentService()
        agent_id = uuid4()
        
        result = await service.destroy_agent(agent_id)
        
        assert result["status"] == AgentStatus.STOPPED


class TestAgentPermissions:
    """Test agent permission system."""
    
    def test_main_agent_permissions(self):
        """Test main agent has full permissions."""
        service = AgentService()
        
        perms = service.get_agent_permissions(AgentType.MAIN)
        
        assert perms["can_execute_commands"] is True
        assert perms["can_create_bots"] is True
        assert perms["can_allocate_tokens"] is True
        assert "email" in perms["allowed_channels"]
        assert "sms" in perms["allowed_channels"]
    
    def test_bot_agent_permissions(self):
        """Test bot agent has limited permissions."""
        service = AgentService()
        
        perms = service.get_agent_permissions(AgentType.BOT)
        
        assert perms["can_execute_commands"] is True
        assert perms["can_write_files"] is False
        assert perms["can_create_bots"] is False
        assert perms["can_install_packages"] is False
    
    def test_messenger_agent_permissions(self):
        """Test messenger agent has minimal permissions."""
        service = AgentService()
        
        perms = service.get_agent_permissions(AgentType.MESSENGER)
        
        assert perms["can_execute_commands"] is False
        assert perms["can_read_files"] is False
        assert perms["can_send_messages"] is True


class TestTokenRequests:
    """Test bot token request system."""
    
    @pytest.mark.asyncio
    async def test_request_tokens(self):
        """Test bot requesting tokens from parent."""
        service = AgentService()
        bot_id = uuid4()
        parent_id = uuid4()
        
        request = await service.request_tokens(
            bot_id=bot_id,
            parent_agent_id=parent_id,
            amount=50,
            reason="Need more tokens for email campaign",
        )
        
        assert request["bot_id"] == bot_id
        assert request["parent_agent_id"] == parent_id
        assert request["amount"] == 50
        assert request["status"] == "pending"
