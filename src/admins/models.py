import uuid

from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[bytes] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
