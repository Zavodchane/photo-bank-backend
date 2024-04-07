from pydantic import BaseModel


class TagCreated(BaseModel):
    tag_name: str


class TagOut(TagCreated):
    pass
