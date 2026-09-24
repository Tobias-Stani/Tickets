from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field, StringConstraints

from app.modules.users.models import Role

NormalizedEmail = Annotated[EmailStr, AfterValidator(str.lower)]
FullName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
Password = Annotated[str, Field(min_length=8, max_length=128)]


class UserCreate(BaseModel):
    email: NormalizedEmail
    full_name: FullName
    password: Password
    role: Role = Role.CLIENT
    tag_ids: list[int] = []


class UserUpdate(BaseModel):
    email: NormalizedEmail
    full_name: FullName
    role: Role
    tag_ids: list[int] = []


class PasswordReset(BaseModel):
    password: Password
