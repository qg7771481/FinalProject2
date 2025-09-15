from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.utils.dependencies import get_db
from app.models.user import User
from app.schemas.auth import RegisterIn, TokenOut
from app.schemas.user import UserOut
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserOut,
    summary="Реєстрація нового користувача",
    description="""
Створює нового користувача в системі.

- Перевіряє, чи **username** або **email** вже існують у базі.
- Якщо існують — повертає помилку `400`.
- Якщо все добре — зберігає нового користувача та повертає його дані.
""",
    responses={
        201: {"description": "Користувач успішно створений", "model": UserOut},
        400: {"description": "Username або email вже зайнято"},
    },
    status_code=201,
)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username або email вже зайнято")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, username=user.username, email=user.email, created_at=user.created_at)


@router.post(
    "/token",
    response_model=TokenOut,
    summary="Отримати JWT токен (логін)",
    description="""
Аутентифікація користувача за допомогою **username** та **password**.

- Перевіряє, чи існує користувач у базі.
- Якщо логін або пароль невірні — повертає помилку `401 Unauthorized`.
- Якщо все правильно — генерує та повертає **JWT токен** для доступу до захищених роутів.
""",
    responses={
        200: {"description": "Успішна автентифікація. Повертається JWT токен", "model": TokenOut},
        401: {"description": "Невірні креденшіали (логін або пароль)"},
    },
)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірні креденшіали")
    token = create_access_token({"sub": str(user.id)})
    return TokenOut(access_token=token)
