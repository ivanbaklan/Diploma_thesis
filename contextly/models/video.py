from uuid import UUID, uuid4

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model

from contextly.models.user import User


class Video(Model):
    id: UUID = fields.UUIDField(primary_key=True, default=uuid4)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        model_name="models.User", related_name="videos"
    )
    url: str = fields.CharField(max_length=2048, unique=True)
    title: str = fields.CharField(max_length=2048, default="")
    description: str = fields.TextField(default="")
    text: str = fields.TextField(default="")
    status: str = fields.CharField(max_length=128, default="create")
    audio_chunks: int = fields.IntField(default=0)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}-{self.title}"

    class Meta:
        table = "videos"


VideoSchema = pydantic_model_creator(Video)
