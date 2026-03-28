



from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
import csv
from io import StringIO



# from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session



from database import SessionLocal, engine
from models import Base, User, Transaction
from schemas import RegisterRequest, LoginRequest, TransactionRequest
from auth import hash_pin, verify_pin

app = FastAPI()

# 🔥 CORS (React connect karne ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 DB Tables create
Base.metadata.create_all(bind=engine)

# 🔥 Dependency (DB session)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🏠 Home
@app.get("/")
def home():
    return {"message": "Smart ATM Backend Running 🚀"}

# 📝 Register
@app.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.card_number == user.card_number).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Card already exists")

    new_user = User(
        name=user.name,
        card_number=user.card_number,
        pin_hash=hash_pin(user.pin),
        balance=0.0
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/bulk-register")
def bulk_register(users: list[RegisterRequest], db: Session = Depends(get_db)):
    added_users = []

    for user in users:
        existing_user = db.query(User).filter(User.card_number == user.card_number).first()
        
        if not existing_user:
            new_user = User(
                name=user.name,
                card_number=user.card_number,
                pin_hash=hash_pin(user.pin),
                balance=0.0
            )
            db.add(new_user)
            added_users.append(user.card_number)

    db.commit()

    return {
        "message": "Bulk users added",
        "users_added": added_users
    }





#  (CSV API)
@app.post("/upload-csv")
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(contents))

    added_users = []

    for row in csv_reader:
        existing_user = db.query(User).filter(User.card_number == row["card_number"]).first()

        if not existing_user:
            new_user = User(
                name=row["name"],
                card_number=row["card_number"],
                pin_hash=hash_pin(row["pin"]),
                balance=0.0
            )
            db.add(new_user)
            added_users.append(row["card_number"])

    db.commit()

    return {
        "message": "CSV users added",
        "users_added": added_users
    }



# 🔐 Login
@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.card_number == data.card_number).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_pin(data.pin, user.pin_hash):
        raise HTTPException(status_code=401, detail="Incorrect PIN")

    return {
        "message": "Login successful",
        "name": user.name,
        "balance": user.balance
    }

# 💰 Deposit
@app.post("/deposit")
def deposit(data: TransactionRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.card_number == data.card_number).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    user.balance += data.amount

    txn = Transaction(
        card_number=data.card_number,
        type="deposit",
        amount=data.amount
    )

    db.add(txn)
    db.commit()

    return {
        "message": "Amount deposited successfully",
        "new_balance": user.balance
    }

# 💸 Withdraw
@app.post("/withdraw")
def withdraw(data: TransactionRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.card_number == data.card_number).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    if data.amount > user.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    user.balance -= data.amount

    txn = Transaction(
        card_number=data.card_number,
        type="withdraw",
        amount=data.amount
    )

    db.add(txn)
    db.commit()

    return {
        "message": "Withdrawal successful",
        "new_balance": user.balance
    }

# 📜 Transactions History
@app.get("/transactions")
def get_transactions(card_number: str, db: Session = Depends(get_db)):
    txns = db.query(Transaction).filter(
        Transaction.card_number == card_number
    ).order_by(Transaction.timestamp.desc()).all()

    return txns