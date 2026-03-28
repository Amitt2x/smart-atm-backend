from pydantic import BaseModel

class RegisterRequest(BaseModel):
    name: str
    card_number: str
    pin: str

class LoginRequest(BaseModel):
    card_number: str
    pin: str

class TransactionRequest(BaseModel):
    card_number: str
    amount: float