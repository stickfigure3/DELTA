"""Command execution routes."""

from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ExecRequest(BaseModel):
    command: str
    working_dir: str = "/workspace"
    timeout_seconds: int = 300
    env_vars: dict[str, str] | None = None


@router.post("/{sandbox_id}/exec")
async def execute_command(sandbox_id: UUID, request: ExecRequest) -> dict:
    """Execute a command in a sandbox."""
    return {
        "sandbox_id": str(sandbox_id),
        "command": request.command,
        "exit_code": 0,
        "stdout": "",
        "stderr": "",
        "duration_ms": 0,
    }


@router.get("/{sandbox_id}/exec/{exec_id}")
async def get_execution_result(sandbox_id: UUID, exec_id: str) -> dict:
    """Get the result of a command execution."""
    return {
        "id": exec_id,
        "sandbox_id": str(sandbox_id),
        "status": "completed",
        "exit_code": 0,
    }
