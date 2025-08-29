from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from app.models.skill import Skill
from app.models.user import User
from app.schemas.skill import SkillCreate, SkillOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post("/", response_model=SkillOut, summary="Створити навичку")
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    existing = db.query(Skill).filter(Skill.name == skill.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Така навичка вже існує")
    new_skill = Skill(name=skill.name)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.post("/add/{skill_id}", summary="Додати навичку користувачу")
def add_skill_to_user(
        skill_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill не знайдено")

    current_user.skills.append(skill)
    db.commit()
    return {"message": f"Навичка {skill.name} додана користувачу {current_user.username}"}


@router.get("/my", response_model=list[SkillOut], summary="Отримати свої навички")
def get_my_skills(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return current_user.skills
