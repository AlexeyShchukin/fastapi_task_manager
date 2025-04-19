from pydantic import BaseModel


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPairResponse(AccessTokenResponse):
    refresh_token: str
