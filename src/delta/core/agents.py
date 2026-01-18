"""Agent lifecycle management service."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from delta.models.agent import AgentConfig, AgentStatus, AgentType


class AgentService:
    """
    Manage agent lifecycle: creation, execution, pausing, destruction.
    
    Agent Hierarchy:
    - Main Agent: Full permissions, can create bots, allocate tokens
    - Bot Agent: Limited permissions, specific task, requests tokens from main
    - Messenger Bot: Ultra-limited, can only send pre-approved messages
    """
    
    def __init__(self):
        self.default_config = AgentConfig()
    
    async def create_agent(
        self,
        user_id: UUID,
        name: str,
        agent_type: AgentType = AgentType.MAIN,
        config: Optional[AgentConfig] = None,
        parent_agent_id: Optional[UUID] = None,
    ) -> dict:
        """
        Create a new agent.
        
        For MAIN agents: Full sandbox with all capabilities
        For BOT agents: Restricted sandbox with limited permissions
        """
        if config is None:
            config = self.default_config
        
        agent_id = uuid4()
        
        # Prepare agent data
        agent_data = {
            "id": agent_id,
            "user_id": user_id,
            "parent_agent_id": parent_agent_id,
            "name": name,
            "agent_type": agent_type,
            "status": AgentStatus.CREATING,
            "template": config.template,
            "memory_mb": config.memory_mb,
            "cpu_cores": config.cpu_cores,
            "token_budget": config.token_budget,
            "tokens_used": 0,
            "created_at": datetime.utcnow(),
        }
        
        # TODO: Create Fly.io machine
        # machine = await self.fly_client.create_machine(...)
        # agent_data["fly_machine_id"] = machine.id
        # agent_data["fly_app_name"] = machine.app_name
        
        agent_data["status"] = AgentStatus.RUNNING
        
        return agent_data
    
    async def create_bot(
        self,
        user_id: UUID,
        parent_agent_id: UUID,
        name: str,
        task_description: str,
        allowed_channels: list[str],
        token_budget: int = 50,
        max_messages_per_day: int = 10,
    ) -> dict:
        """
        Create a bot agent with limited permissions.
        
        Bots:
        - Have a specific task they can perform
        - Limited to certain communication channels
        - Can only use pre-approved message templates
        - Must request tokens from parent agent
        """
        bot_id = uuid4()
        
        bot_data = {
            "id": bot_id,
            "user_id": user_id,
            "parent_agent_id": parent_agent_id,
            "name": name,
            "agent_type": AgentType.BOT,
            "status": AgentStatus.RUNNING,
            "task_description": task_description,
            "allowed_channels": allowed_channels,
            "token_budget": token_budget,
            "tokens_used": 0,
            "max_messages_per_day": max_messages_per_day,
            "created_at": datetime.utcnow(),
        }
        
        return bot_data
    
    async def pause_agent(self, agent_id: UUID) -> dict:
        """Pause an agent, preserving its state."""
        # TODO: Pause Fly.io machine
        return {
            "id": agent_id,
            "status": AgentStatus.PAUSED,
            "paused_at": datetime.utcnow(),
        }
    
    async def resume_agent(self, agent_id: UUID) -> dict:
        """Resume a paused agent."""
        # TODO: Resume Fly.io machine
        return {
            "id": agent_id,
            "status": AgentStatus.RUNNING,
            "resumed_at": datetime.utcnow(),
        }
    
    async def destroy_agent(self, agent_id: UUID) -> dict:
        """Destroy an agent and release resources."""
        # TODO: Destroy Fly.io machine
        return {
            "id": agent_id,
            "status": AgentStatus.STOPPED,
            "destroyed_at": datetime.utcnow(),
        }
    
    async def execute_command(
        self,
        agent_id: UUID,
        command: str,
        working_dir: str = "/workspace",
        timeout_seconds: int = 300,
    ) -> dict:
        """Execute a command in the agent's sandbox."""
        # TODO: Execute via Fly.io machine
        return {
            "agent_id": agent_id,
            "command": command,
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
            "duration_ms": 0,
        }
    
    async def request_tokens(
        self,
        bot_id: UUID,
        parent_agent_id: UUID,
        amount: int,
        reason: str,
    ) -> dict:
        """
        Bot requests more tokens from parent agent.
        
        Flow:
        1. Bot sends request with reason
        2. Parent agent (or user) reviews
        3. If approved, tokens are transferred
        """
        request_id = uuid4()
        
        return {
            "id": request_id,
            "bot_id": bot_id,
            "parent_agent_id": parent_agent_id,
            "amount": amount,
            "reason": reason,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
    
    def get_agent_permissions(self, agent_type: AgentType) -> dict:
        """Get the permission set for an agent type."""
        if agent_type == AgentType.MAIN:
            return {
                "can_execute_commands": True,
                "can_read_files": True,
                "can_write_files": True,
                "can_install_packages": True,
                "can_create_bots": True,
                "can_allocate_tokens": True,
                "can_send_messages": True,
                "allowed_channels": ["email", "sms", "voice_call"],
                "can_access_network": True,
            }
        elif agent_type == AgentType.BOT:
            return {
                "can_execute_commands": True,
                "can_read_files": True,
                "can_write_files": False,
                "can_install_packages": False,
                "can_create_bots": False,
                "can_allocate_tokens": False,
                "can_send_messages": True,
                "allowed_channels": [],  # Set per-bot
                "can_access_network": False,
            }
        else:  # MESSENGER
            return {
                "can_execute_commands": False,
                "can_read_files": False,
                "can_write_files": False,
                "can_install_packages": False,
                "can_create_bots": False,
                "can_allocate_tokens": False,
                "can_send_messages": True,
                "allowed_channels": [],  # Set per-bot
                "can_access_network": False,
            }
