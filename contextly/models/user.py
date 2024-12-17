from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.models import Model


class User(Model):
    id: int = fields.IntField(primary_key=True)
    username: str = fields.CharField(max_length=512, unique=True)
    hashed_password: str = fields.CharField(max_length=512)
    email: str = fields.CharField(max_length=512, unique=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        table = "users"


UserSchema = pydantic_model_creator(User)
