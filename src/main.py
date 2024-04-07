from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.admins.router import router as admins_router
from src.tags.router import router as tags_router
from src.tasks.router import router as tasks_router
from src.photos.router import router as photos_router
from src.config import settings


app = FastAPI(
    title=settings.app.title,
    root_path=settings.app.prefix,
)

app.include_router(
    router=admins_router,
    prefix="/admins",
    tags=["Admins"],
)

app.include_router(
    router=tags_router,
    prefix="/tags",
    tags=["Tags"],
)

app.include_router(
    router=tasks_router,
    prefix="/tasks",
    tags=["Tasks"],
)

app.include_router(
    router=photos_router,
    prefix="/photos",
    tags=["Photos"],
)

origins: list = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
