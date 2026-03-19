from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class MessageURL(Base):
    __tablename__ = "msg_urls"
    url_code: Mapped[str] = mapped_column(primary_key=True)
    message_text: Mapped[str] = mapped_column(nullable=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    files: Mapped[list["Files"]] = relationship("Files", back_populates="message")


class Files(Base):
    __tablename__ = "msg_files"
    filepath: Mapped[str] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(nullable=True)
    url_code: Mapped[str] = mapped_column(
        ForeignKey("msg_urls.url_code"), nullable=False
    )
    message: Mapped["MessageURL"] = relationship("MessageURL", back_populates="files")
