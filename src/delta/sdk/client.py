"""DELTA SDK Client implementation."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from uuid import UUID

import httpx

from delta.sdk.models import (
    Agent,
    AgentConfig,
    AgentStatus,
    ExecResult,
    FileContent,
    FileInfo,
    MessageResult,
    Sandbox,
    SandboxConfig,
    TokenBudget,
)


class DeltaError(Exception):
    """Base exception for DELTA SDK errors."""
    pass


class AgentNotFoundError(DeltaError):
    """Raised when an agent is not found."""
    pass


class InsufficientTokensError(DeltaError):
    """Raised when there aren't enough tokens."""
    pass


class FileOperations:
    """File operations for a sandbox."""

    def __init__(self, agent: DeltaAgent) -> None:
        self._agent = agent

    async def read(self, path: str) -> str:
        """Read a file from the sandbox."""
        response = await self._agent._client._request(
            "GET",
            f"/v1/sandboxes/{self._agent._sandbox_id}/files/{path.lstrip('/')}",
        )
        return FileContent(**response).content

    async def write(self, path: str, content: str) -> None:
        """Write content to a file in the sandbox."""
        await self._agent._client._request(
            "PUT",
            f"/v1/sandboxes/{self._agent._sandbox_id}/files/{path.lstrip('/')}",
            json={"content": content},
        )

    async def delete(self, path: str) -> None:
        """Delete a file from the sandbox."""
        await self._agent._client._request(
            "DELETE",
            f"/v1/sandboxes/{self._agent._sandbox_id}/files/{path.lstrip('/')}",
        )

    async def list(self, path: str = "/workspace") -> list[FileInfo]:
        """List files in a directory."""
        response = await self._agent._client._request(
            "GET",
            f"/v1/sandboxes/{self._agent._sandbox_id}/files",
            params={"path": path},
        )
        return [FileInfo(**f) for f in response.get("files", [])]


class MessagingOperations:
    """Messaging operations for an agent."""

    def __init__(self, agent: DeltaAgent) -> None:
        self._agent = agent

    async def send_email(
        self,
        recipient: str,
        subject: str,
        content: str,
        template_id: Optional[str] = None,
    ) -> MessageResult:
        """Send an email."""
        response = await self._agent._client._request(
            "POST",
            "/v1/messaging/email",
            params={"agent_id": str(self._agent.id)},
            json={
                "recipient": recipient,
                "subject": subject,
                "content": content,
                "template_id": template_id,
            },
        )
        return MessageResult(**response)

    async def send_sms(
        self,
        recipient: str,
        content: str,
        template_id: Optional[str] = None,
    ) -> MessageResult:
        """Send an SMS."""
        response = await self._agent._client._request(
            "POST",
            "/v1/messaging/sms",
            params={"agent_id": str(self._agent.id)},
            json={
                "recipient": recipient,
                "content": content,
                "template_id": template_id,
            },
        )
        return MessageResult(**response)

    async def make_call(
        self,
        recipient: str,
        message: str,
        template_id: Optional[str] = None,
    ) -> MessageResult:
        """Make a voice call."""
        response = await self._agent._client._request(
            "POST",
            "/v1/messaging/call",
            params={"agent_id": str(self._agent.id)},
            json={
                "recipient": recipient,
                "message": message,
                "template_id": template_id,
            },
        )
        return MessageResult(**response)


class DeltaAgent:
    """An agent instance."""

    def __init__(self, client: Delta, data: dict, sandbox_id: Optional[str] = None) -> None:
        self._client = client
        self._data = Agent(**data)
        self._sandbox_id = sandbox_id or data.get("sandbox_id")
        self.files = FileOperations(self)
        self.messaging = MessagingOperations(self)

    @property
    def id(self) -> UUID:
        return self._data.id

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def status(self) -> AgentStatus:
        return self._data.status

    @property
    def token_budget(self) -> TokenBudget:
        return TokenBudget(
            total=self._data.token_budget,
            used=self._data.tokens_used,
        )

    async def exec(
        self,
        command: str,
        *,
        timeout_seconds: int = 300,
        working_dir: str = "/workspace",
        env_vars: Optional[dict[str, str]] = None,
    ) -> ExecResult:
        """Execute a command in the agent's sandbox."""
        response = await self._client._request(
            "POST",
            f"/v1/sandboxes/{self._sandbox_id}/exec",
            json={
                "command": command,
                "timeout_seconds": timeout_seconds,
                "working_dir": working_dir,
                "env_vars": env_vars or {},
            },
        )
        return ExecResult(**response)

    async def pause(self) -> None:
        """Pause the agent."""
        await self._client._request("POST", f"/v1/agents/{self.id}/pause")
        self._data.status = AgentStatus.PAUSED

    async def resume(self) -> None:
        """Resume the agent."""
        await self._client._request("POST", f"/v1/agents/{self.id}/resume")
        self._data.status = AgentStatus.RUNNING

    async def destroy(self) -> None:
        """Destroy the agent."""
        await self._client._request("DELETE", f"/v1/agents/{self.id}")

    async def create_bot(
        self,
        name: str,
        task_description: str,
        allowed_channels: list[str] = ["email"],
        token_budget: int = 50,
    ) -> DeltaAgent:
        """Create a bot under this agent."""
        response = await self._client._request(
            "POST",
            f"/v1/agents/{self.id}/bots",
            json={
                "name": name,
                "task_description": task_description,
                "allowed_channels": allowed_channels,
                "token_budget": token_budget,
            },
        )
        return DeltaAgent(self._client, response)

    async def allocate_tokens(self, bot_id: UUID, amount: int) -> None:
        """Allocate tokens to a bot."""
        await self._client._request(
            "POST",
            f"/v1/agents/{self.id}/tokens/allocate",
            params={"bot_id": str(bot_id), "amount": amount},
        )

    async def __aenter__(self) -> DeltaAgent:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.status != AgentStatus.PAUSED:
            await self.destroy()


class DeltaSandbox:
    """A sandbox instance (for backward compatibility)."""

    def __init__(self, client: Delta, data: dict) -> None:
        self._client = client
        self._data = Sandbox(**data)
        self._agent = None

    @property
    def id(self) -> UUID:
        return self._data.id

    async def exec(self, command: str, **kwargs) -> ExecResult:
        response = await self._client._request(
            "POST",
            f"/v1/sandboxes/{self.id}/exec",
            json={"command": command, **kwargs},
        )
        return ExecResult(**response)


class AgentManager:
    """Manager for agent operations."""

    def __init__(self, client: Delta) -> None:
        self._client = client

    async def create(
        self,
        name: str,
        config: Optional[AgentConfig] = None,
    ) -> DeltaAgent:
        """Create a new agent."""
        payload = {"name": name}
        if config:
            payload.update(config.model_dump())
        
        response = await self._client._request("POST", "/v1/agents", json=payload)
        return DeltaAgent(self._client, response)

    async def get(self, agent_id: UUID) -> DeltaAgent:
        """Get an existing agent."""
        response = await self._client._request("GET", f"/v1/agents/{agent_id}")
        return DeltaAgent(self._client, response)

    async def list(self) -> list[DeltaAgent]:
        """List all agents."""
        response = await self._client._request("GET", "/v1/agents")
        return [DeltaAgent(self._client, a) for a in response.get("agents", [])]


class SandboxManager:
    """Manager for sandbox operations (backward compatibility)."""

    def __init__(self, client: Delta) -> None:
        self._client = client

    async def create(self, config: Optional[SandboxConfig] = None) -> DeltaSandbox:
        payload = config.model_dump() if config else {}
        response = await self._client._request("POST", "/v1/sandboxes", json=payload)
        return DeltaSandbox(self._client, response)


class Delta:
    """DELTA SDK client."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.delta-agents.com",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self.agents = AgentManager(self)
        self.sandboxes = SandboxManager(self)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
    ) -> dict:
        client = await self._get_client()
        response = await client.request(method, path, params=params, json=json)

        if response.status_code == 404:
            raise AgentNotFoundError(f"Resource not found: {path}")

        if response.status_code == 402:
            raise InsufficientTokensError("Insufficient tokens")

        response.raise_for_status()

        if response.status_code == 204:
            return {}

        return response.json()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> Delta:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


@asynccontextmanager
async def create_agent(
    api_key: str,
    name: str,
    *,
    config: Optional[AgentConfig] = None,
    base_url: str = "https://api.delta-agents.com",
) -> AsyncGenerator[DeltaAgent, None]:
    """Quick way to create and use an agent."""
    async with Delta(api_key, base_url=base_url) as client:
        agent = await client.agents.create(name, config)
        try:
            yield agent
        finally:
            if agent.status != AgentStatus.PAUSED:
                await agent.destroy()
