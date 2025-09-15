from fastapi import APIRouter, Depends
from app.utils.dependencies import get_current_user
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserOut,
    summary="Поточний користувач (потрібен Bearer токен)",
    description="""
Повертає інформацію про **поточного авторизованого користувача**.

- Необхідна авторизація через **Bearer JWT токен**.
- Повертає дані користувача: `id`, `username`, `email`, `created_at`.
""",
    responses={
        200: {"description": "Інформація про поточного користувача", "model": UserOut},
        401: {"description": "Неавторизований запит (немає або неправильний токен)"},
    },
)
def read_me(current: User = Depends(get_current_user)):
    return current
