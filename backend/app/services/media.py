from __future__ import annotations

import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

MEDIA_ROOT = Path(__file__).resolve().parents[1] / "media"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024  # 8 MB


class MediaError(ValueError):
    pass


def media_url(path: str) -> str:
    """Return a same-origin media URL (relative) so it works behind any tunnel/host.

    Absolute URLs (already-hosted images) pass through unchanged.
    """
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"/media/{path.lstrip('/')}"


async def save_image(file: UploadFile, subdir: str = "products") -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise MediaError("unsupported_image_type")
    ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }[file.content_type]

    target_dir = MEDIA_ROOT / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    dest = target_dir / name

    size = 0
    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 256):
            size += len(chunk)
            if size > MAX_IMAGE_BYTES:
                await out.close()
                dest.unlink(missing_ok=True)
                raise MediaError("image_too_large")
            await out.write(chunk)

    return f"{subdir}/{name}"
