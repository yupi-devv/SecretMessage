from datetime import datetime

from pydantic import BaseModel


class ResponseSuccessMessage(BaseModel):
    url_code: str
    message_text: str | None = None
    expired_at: datetime | None = None
    expired_minutes_delta: int | None = None
    sfiles: None | list[str] = []
    efiles: None | list[str] = []


class ResponseMessage(BaseModel):
    url_code: str
    message_text: str | None = None
    expired_at: datetime | None = None
    files: list[dict[str, str]] | None = None
