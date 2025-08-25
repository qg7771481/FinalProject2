from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.skill import Skill, user_skills
from app.schemas.auth import RegisterIn, TokenOut
from app.schemas.user import UserOut
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut, summary="Реєстрація нового користувача")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    try:
        print("Payload:", payload)

        existing_user = db.query(User).filter(
            (User.username == payload.username) | (User.email == payload.email)
        ).first()
        print("Existing user:", existing_user)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username або email вже зайнято")

        print("Hashing password...")
        password_hash = hash_password(payload.password)
        print("Password hash:", password_hash)

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=password_hash,
        )
        print("Adding user to DB...")
        db.add(user)
        db.commit()
        db.refresh(user)
        print("User created:", user)

        return user

    except Exception as e:
        print("REGISTER ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/token", response_model=TokenOut, summary="Отримати JWT токен (логін)")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірні креденшіали"
        )
    token = create_access_token({"sub": str(user.id)})
    return TokenOut(access_token=token)


@router.post("/register", response_model=UserOut, summary="Реєстрація нового користувача")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    try:
        print("Payload:", payload.dict())
        print("Password type:", type(payload.password))
        print("Password value:", repr(payload.password))

        existing_user = db.query(User).filter(
            (User.username == payload.username) | (User.email == payload.email)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username або email вже зайнято")

        print("Hashing password...")
        password_hash = hash_password(payload.password)
        print("Password hash generated successfully")

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=password_hash,
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        print("User created successfully:", user.id)

        return user

    except HTTPException:
        raise
    except Exception as e:
        print("REGISTER ERROR DETAILS:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error during registration")
