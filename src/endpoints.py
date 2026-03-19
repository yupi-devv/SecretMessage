from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiofiles
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import stg
from src.database.db import get_session
from src.database.models import Files, MessageURL
from src.schemas import ResponseMessage, ResponseSuccessMessage
from src.service import UPLOAD_DIR, generate_unique_code

rtr = APIRouter(prefix="/v1", tags=["Message manipulation"])


@rtr.post("/create")
async def create_message(
    msgtext: str | None = Form(default=""),
    expiry_delta_minutes: str | None = Form(default=""),
    files: list[UploadFile] | None = File(default=None),
    ses: AsyncSession = Depends(get_session),
) -> ResponseSuccessMessage:
    msgtext = msgtext if msgtext != "" else None
    expiry_delta_minutes = (
        int(expiry_delta_minutes) if expiry_delta_minutes != "" else None
    )
    files = files if files != "" else None

    code = generate_unique_code()
    expired_at = (
        (datetime.now() + timedelta(minutes=int(expiry_delta_minutes))).astimezone(
            tz=timezone.utc
        )
        if expiry_delta_minutes is not None
        else None
    )

    if not msgtext and not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text or files required!",
        )

    response = ResponseSuccessMessage(
        url_code=code,
        message_text=msgtext,
        expired_at=expired_at,
        expired_minutes_delta=expiry_delta_minutes,
    )

    saved_files = []
    if files:
        for i, file in enumerate(files):
            try:
                # Store only the relative filename in database
                relative_filename = f"{i}-{code[:9]}{Path(file.filename).suffix}"
                file_location = UPLOAD_DIR.absolute() / relative_filename

                async with aiofiles.open(file_location, "wb") as ff:
                    while chunk := await file.read(1048576):
                        await ff.write(chunk)

                saved_files.append(
                    Files(
                        filename=file.filename,
                        filepath=relative_filename,
                        url_code=code,
                    )
                )
                response.sfiles.append(file.filename)
            except Exception:
                response.efiles.append(file.filename)
        if saved_files:
            ses.add_all(saved_files)

    message = MessageURL(message_text=msgtext, url_code=code, expired_at=expired_at)
    ses.add(message)

    await ses.commit()
    await ses.refresh(message)

    return response


@rtr.get("/view/{url_code}")
async def view_message(
    req: Request,
    url_code: str,
    ses: AsyncSession = Depends(get_session),
):
    current_time = datetime.now(tz=timezone.utc)
    res = await ses.execute(
        select(MessageURL)
        .where(MessageURL.url_code == url_code)
        .options(selectinload(MessageURL.files))
    )
    result = res.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found!"
        )

    # Handle timezone-aware/naive datetime comparison
    if result.expired_at is not None:
        expired_at = result.expired_at
        # If expired_at is naive, assume it's UTC
        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)

        if expired_at <= current_time:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found!"
            )
    files_info = []
    for f in result.files:
        # Build base URL
        base_url = (
            str(req.base_url)
            if stg.MODE == "TEST"
            else f"https://{stg.BASE_URL}/"
            if stg.MODE == "PROD"
            else str(req.base_url)
        )
        # Remove trailing slash if present
        base_url = base_url.rstrip("/")

        files_info.append(
            {
                "filename": f.filename,
                "download_url": f"{base_url}/v1/download/{f.filepath}",
            }
        )

    return ResponseMessage(
        url_code=result.url_code,
        message_text=result.message_text,
        expired_at=result.expired_at,
        files=files_info,
    )


async def file_stream(file_path: Path):
    async with aiofiles.open(file_path, mode="rb") as file:
        while chunk := await file.read(1048576):
            yield chunk


@rtr.get("/download/{filepath:path}")
async def download_file(filepath: str, ses: AsyncSession = Depends(get_session)):
    # Reconstruct full path from relative filename
    full_filepath = UPLOAD_DIR.absolute() / filepath

    # First try to find by relative path
    res = await ses.execute(
        select(Files)
        .where(Files.filepath == filepath)
        .options(selectinload(Files.message))
    )
    result = res.scalar_one_or_none()

    # If not found, try to find by full path (for backward compatibility)
    if not result:
        res = await ses.execute(
            select(Files)
            .where(Files.filepath == str(full_filepath))
            .options(selectinload(Files.message))
        )
        result = res.scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found in database"
        )

    if not result.message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Associated message not found"
        )

    current_time = datetime.now(timezone.utc)

    # Handle timezone-aware/naive datetime comparison
    if result.message.expired_at is not None:
        expired_at = result.message.expired_at
        # If expired_at is naive, assume it's UTC
        if expired_at.tzinfo is None:
            expired_at = expired_at.replace(tzinfo=timezone.utc)

        if expired_at <= current_time:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="File has expired"
            )

    if not full_filepath.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found!"
        )

    import os

    file_size = os.path.getsize(full_filepath)

    return StreamingResponse(
        file_stream(full_filepath),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{result.filename}"',
            "Content-Length": str(file_size),
        },
    )
