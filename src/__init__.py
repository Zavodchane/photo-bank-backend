__all__ = (
    "Base",
    "Admin",
    "Photo",
    "Identical",
    "PhotosTags",
    "Tag",
)


from src.models import Base
from src.admins.models import Admin
from src.photos.models import Photo, Identical
from src.tags.models import Tag, PhotosTags
