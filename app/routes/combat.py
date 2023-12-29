import random
from app.models import User

from typing import Optional


def combat_function(enemy_strength: int, user_id: int, db, fatigue: Optional[bool] = False,
                    hangover: Optional[bool] = False, dysmoral: Optional[bool] = False):
    """Боевка игры, учитывает силу противника и необязательные параметры состояния"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Пользователь не найден")

    player_attack_info = []
    enemy_attack_info = []
    player_attack_info.append("Вы бросаете вызов вашему врагу!")

    while user.health > 0 and enemy_strength > 0:
        player_attack = random.randint(10, 20)
        enemy_attack = random.randint(5, 20)

        # Учет бонусов на основе состояния персонажа
        if fatigue:
            player_attack -= 5
        if hangover:
            player_attack -= 5
        if dysmoral:
            player_attack -= 5

        enemy_strength -= player_attack
        user.health -= enemy_attack

        db.commit()

        player_attack_info.append(f"Вы нанесли {player_attack} урона. У противника осталось {enemy_strength} HP.")
        enemy_attack_info.append(f"Противник нанес {enemy_attack} урона. У вас осталось {user.health} HP.")

    if user.health > 0:
        player_attack_info.append("Вы победили в сражении!")
        player_attack_info.append("=" * 50)
        user.gold += 10
        db.commit()
        return "Победа! Вы одолели противника.", player_attack_info, enemy_attack_info
    else:
        player_attack_info.append("Вы проиграли. Ваше приключение окончено.")
        return "Поражение! Ваше приключение окончено.", player_attack_info, enemy_attack_info
