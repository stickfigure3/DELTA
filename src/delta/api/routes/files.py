"""File operation routes."""

from uuid import UUID
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class WriteFileRequest(BaseModel):
    content: str


@router.get("/{sandbox_id}/files")
async def list_files(sandbox_id: UUID, path: str = "/workspace") -> dict:
    """List files in a directory."""
    return {"path": path, "files": []}


@router.get("/{sandbox_id}/files/{path:path}")
async def read_file(sandbox_id: UUID, path: str) -> dict:
    """Read a file."""
    return {"path": path, "content": ""}


@router.put("/{sandbox_id}/files/{path:path}")
async def write_file(sandbox_id: UUID, path: str, request: WriteFileRequest) -> dict:
    """Write to a file."""
    return {"path": path, "size": len(request.content)}


@router.delete("/{sandbox_id}/files/{path:path}")
async def delete_file(sandbox_id: UUID, path: str) -> dict:
    """Delete a file."""
    return {"message": f"Deleted {path}"}
