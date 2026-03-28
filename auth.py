import bcrypt

def hash_pin(pin: str):
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

def verify_pin(pin: str, hashed_pin: str):
    return bcrypt.checkpw(pin.encode(), hashed_pin.encode())