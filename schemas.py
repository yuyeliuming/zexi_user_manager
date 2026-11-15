from pydantic import BaseModel,Field
class UserAuth(BaseModel):
    username: str = Field(min_length=1,max_length=64)
    password: str = Field(min_length=1,max_length=64)
class UsernameUpdate(BaseModel):
    new_username: str = Field(min_length=1,max_length=64)
class PasswordUpdate(BaseModel):
    old_password: str = Field(min_length=1,max_length=64)
    new_password: str = Field(min_length=1,max_length=64)
class Token(BaseModel):
    access_token: str
    token_type: str