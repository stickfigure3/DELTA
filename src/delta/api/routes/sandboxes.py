"""Sandbox management routes."""

from uuid import UUID
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_sandbox() -> dict:
    """Create a new sandbox."""
    return {"id": "placeholder", "status": "creating"}


@router.get("/")
async def list_sandboxes() -> dict:
    """List all sandboxes."""
    return {"sandboxes": [], "total": 0}


@router.get("/{sandbox_id}")
async def get_sandbox(sandbox_id: UUID) -> dict:
    """Get sandbox details."""
    return {"id": str(sandbox_id), "status": "running"}


@router.delete("/{sandbox_id}")
async def delete_sandbox(sandbox_id: UUID) -> dict:
    """Delete a sandbox."""
    return {"message": "Sandbox deleted"}


@router.post("/{sandbox_id}/pause")
async def pause_sandbox(sandbox_id: UUID) -> dict:
    """Pause a sandbox."""
    return {"id": str(sandbox_id), "status": "paused"}


@router.post("/{sandbox_id}/resume")
async def resume_sandbox(sandbox_id: UUID) -> dict:
    """Resume a sandbox."""
    return {"id": str(sandbox_id), "status": "running"}
