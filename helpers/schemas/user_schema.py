from pydantic import BaseModel


class User(BaseModel):
    user_id: int
    email: str
    phone_number: str
    address: str
    state: str
    country: str
    password: str

    is_active: bool
    is_admin: bool
    is_staff: bool
    is_vendor: bool
    is_customer: bool


class APIKey:
    user: User
    api_key: str
