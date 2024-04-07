from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base

if TYPE_CHECKING:
    from src.photos.models import Photo


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    photos: Mapped[list["Photo"]] = relationship(
        secondary="photo_tag",
        back_populates="tags",
    )


class PhotosTags(Base):
    __tablename__ = "photo_tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"))
    photo_id: Mapped[int] = mapped_column(ForeignKey("photo.id"))
