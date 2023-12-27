import random
from config import character_state

# Функция битвы с противником
def combat(enemy_strength):
    """Боевка игры, учитываются, принимает enemy_strength = сила противника"""
    global character_state
    print("Вы бросаете вызов вашему врагу!")
    while character_state['health'] > 0 and enemy_strength > 0:
        player_attack = random.randint(10, 20)
        enemy_attack = random.randint(5, 20)
        enemy_strength -= player_attack
        character_state['health'] -= enemy_attack
        print(f"Вы нанесли {player_attack} урона. У противника осталось {enemy_strength} HP.")
        print(f"Противник нанес {enemy_attack} урона. У вас осталось {character_state['health']} HP.")
    if character_state['health'] > 0:
        print("Вы победили в сражении!")
        print("=" * 100)
        return True
    else:
        print("Вы проиграли. Ваше приключение окончено.")
        print("=" * 100)
        return False