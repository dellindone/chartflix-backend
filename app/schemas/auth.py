from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    fullname: str
    phone: str

class SignInRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str
    # token_type:str = "bearer"

class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str

class LogoutRequest(BaseModel):
    refresh_token: str

class LogoutResponse(BaseModel):
    message: str