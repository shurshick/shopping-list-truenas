from datetime import datetime

from pydantic import ConfigDict
from pydantic import BaseModel, EmailStr, Field


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PublicServerConfig(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    app_name: str
    external_url: str
    allow_registration: bool
    setup_completed: bool


class ListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ListUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    quantity: str = Field(default="", max_length=80)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    quantity: str | None = Field(default=None, max_length=80)
    is_checked: bool | None = None


class ShareRequest(BaseModel):
    email: EmailStr


class ListMemberResponse(BaseModel):
    id: int
    email: EmailStr
    is_owner: bool


class MembersResponse(BaseModel):
    members: list[ListMemberResponse]


class InviteResponse(BaseModel):
    token: str
    url: str
    app_url: str
    expires_at: datetime | None = None


class SyncItem(BaseModel):
    id: int
    name: str
    quantity: str
    is_checked: bool
    updated_at: datetime


class SyncList(BaseModel):
    id: int
    name: str
    owner_id: int
    updated_at: datetime
    items: list[SyncItem]


class SyncResponse(BaseModel):
    lists: list[SyncList]
