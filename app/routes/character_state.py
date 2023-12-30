from fastapi import APIRouter
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.models import User

router = APIRouter()


def get_character_state(user_id: int, db: Session) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Пользователь не найден")
    db.commit()
    character_state = {
        "health": user.health,
        "max_hp": user.max_hp,
        "gold": user.gold,
        "fatigue": user.fatigue,
        "hangover": user.hangover,
        "dysmoral": user.dysmoral
    }
    print('get_character_state', character_state)
    return character_state


def update_character_state(user_id: int, db: Session, character_state: dict):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Пользователь не найден")

    for key, val in character_state.items():
        setattr(user, key, val)
    db.commit()


def get_user_from_database(name: str):
    db = SessionLocal()
    user = db.query(User).filter(User.name == name).first()
    db.close()
    return user


def reset_character_state(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Пользователь не найден")
    user.health = 100
    user.max_hp = 100
    user.gold = 5
    user.fatigue = False
    user.hangover = False
    user.dysmoral = False
    db.add(user)
    db.commit()