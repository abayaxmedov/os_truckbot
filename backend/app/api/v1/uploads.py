from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.deps import CurrentUser
from app.services.media import MediaError, media_url, save_image

router = APIRouter(prefix="/uploads", tags=["uploads"])


class UploadOut(BaseModel):
    path: str
    url: str


@router.post("/image", response_model=UploadOut)
async def upload_image(
    user: CurrentUser,
    file: UploadFile = File(...),
    subdir: str = "misc",
) -> UploadOut:
    safe_subdir = subdir if subdir in ("misc", "banners", "products", "brands") else "misc"
    try:
        path = await save_image(file, subdir=safe_subdir)
    except MediaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return UploadOut(path=path, url=media_url(path))
