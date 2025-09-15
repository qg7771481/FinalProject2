from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.matching import find_matches_for_user, save_match_in_db

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get(
    "/find",
    summary="Знайти користувачів зі схожими навичками",
    description="""
Повертає список користувачів, які мають навички, схожі на навички поточного користувача.

- Використовує функцію `find_matches_for_user`.
- Потрібна авторизація (поточний користувач отримується через токен).
""",
    responses={
        200: {"description": "Список користувачів зі схожими навичками"},
        401: {"description": "Неавторизований запит (немає або неправильний токен)"},
    },
)
def find_matches(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return find_matches_for_user(db, current_user)


@router.post(
    "/save/{user_id}",
    summary="Зберегти match у базі",
    description="""
Зберігає користувача з `user_id` як match для поточного користувача.

- Використовує функцію `save_match_in_db`.
- Потрібна авторизація.
- Повертає результат збереження (успішно чи ні).
""",
    responses={
        200: {"description": "Match успішно збережено"},
        400: {"description": "Помилка збереження (наприклад, match вже існує)"},
        401: {"description": "Неавторизований запит (немає або неправильний токен)"},
        404: {"description": "Користувача з таким user_id не знайдено"},
    },
)
def save_match(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return save_match_in_db(db, current_user, user_id)
