from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.matching import find_matches_for_user, save_match_in_db

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/find", summary="Знайти користувачів зі схожими навичками")
def find_matches(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return find_matches_for_user(db, current_user)


@router.post("/save/{user_id}", summary="Зберегти match у базі")
def save_match(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return save_match_in_db(db, current_user, user_id)
