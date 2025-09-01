from sqlalchemy.orm import Session
from app.models.user import User
from app.models.matches import Match


def find_matches_for_user(db: Session, current_user: User):
    my_skills = {s.id for s in current_user.skills}
    if not my_skills:
        return {"message": "У тебе ще немає навичок"}

    users = db.query(User).filter(User.id != current_user.id).all()

    matches = []
    for u in users:
        other_skills = {s.id for s in u.skills}
        common = my_skills & other_skills
        if common:
            matches.append({
                "user_id": u.id,
                "username": u.username,
                "common_skills": [s.name for s in u.skills if s.id in common]
            })

    return {"matches": matches}


def save_match_in_db(db: Session, current_user: User, user_id: int):
    new_match = Match(user1_id=current_user.id, user2_id=user_id)
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return {"message": "Матч збережено", "match_id": new_match.id}
