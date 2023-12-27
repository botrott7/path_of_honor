import random
def river_adventure():
    """Ветка РЕКА, путь по выбору река, ветка викингов"""
    print("Подойдя к реке, вы обнаруживаете группу викингов, которые усердно готовят свои драккары к отплытию")
    print("Викинги вас заметили и предложили отправиться с ними, предлагая вам сделку")
    print("Если вы одолеете воина, то отправитесь с ними беслатно, если проиграете, то отдадите всё свое золото!")
    choice = make_choice("Будете сражаться или попытаетесь сбежать?",
                         ["Сражаться", "Сбежать", "Предложить золото"])
    global character_state

    if choice == 1:
        print("Вы смело бросаетесь в бой...")
        if combat(enemy_strength=60):
            print("Победа! Вы одолели викинга и нашли небольшое количество золота.")
            character_state['gold'] += 5
            river_rest_or_move()
        else:
            return

    elif choice == 2:
        print("Вы быстро убегаете и вас не настигает никакой враг.")

    else:
        character_state['gold'] -= 5
        print("Вы отдаете викингам всё свое золото, они с пренебрежением пускают вас на корабль!")
        river_rest_or_move()
    continue_adventure()  # Возвращаем игрока к выбору пути.


def river_rest_or_move():
    """Ветка РЕКА, игрок может получить отрицательный эффект 'похмелье'"""
    global character_state
    print("Викинги на корабле предлагают соревнование: кто выпьет больше пива!")
    choice = make_choice("Желаете принять участие?",
                         ["Принять", "Отказаться"])

    if choice == 1:
        print("Вы решаете принять участие в празднике пива!")
        success = random.choice([True, False])

        if success:
            print("К неожиданности всех, вы оказываетесь несгибаемым пивным воином!"
                  " Поражая своим талантом, вы удостаиваетесь главного приза.")
            character_state["gold"] += 10
            character_state['hangover'] = True
        else:
            if character_state["gold"] >= 0:
                print("Увы, это сражение оказалось не по вашим силам."
                      " Вам пришлось раскошелиться, чтобы оплатить счет за участие.")
                print(" Также вы чувствуете себя довольно нехорошо...")
                character_state["gold"] -= 5
                character_state['hangover'] = True
            else:
                end_game("У вас не хватает золота, чтобы оплатить участие!"
                         " Разгневанные викинги швыряют вас за борт!")

    else:
        print("Предпочитая остаться вне сражения, вы наслаждаетесь зрелищем,"
              " встречаете новых друзей и выигрываете пару мелких дружеских пари на исход сражений."
              " В это время ваш дух праздника и ваш кошелек только укрепляются.")
    army_vikings()


def army_vikings():
    """Ветка РЕКА, битва героя на стороне викикингов"""
    global character_state
    print("Во главе корабля стоит величественный викинг и задаёт вам вопрос:")
    print("Готовы ли вы присоединиться к их стороне в предстоящей битве.")
    choice = make_choice("Принимаете ли вы предложение викингов?",
                         ["Принять", "Отказаться"])

    if choice == 1 or (choice == 2 and character_state["gold"] < 5):
        if choice == 2:
            print("У вас не хватает золота на уплату,"
                  "поэтому викинги принудительно отправляют вас воевать на своей стороне.")
            character_state["dysmoral"] = True

        if character_state["gold"] >= 5:
            print("Перед битвой вам предложили эликсир, который поможет вам в сражении. Стоимость эликсира: 5 золотых.")
            buy_potion = make_choice("Купите ли вы эликсир?", ["Купить", "Не покупать"])
            if buy_potion == 1:
                print("Вы приобретаете эликсир!")
                character_state["gold"] -= 5
                character_state["health"] = 100
            else:
                print("Вы решаете не тратить деньги на эликсир.")
        else:
            print("У вас недостаточно золота для покупки эликсира.")

        print("Вы соглашаетесь сражаться вместе с викингами.")
        if character_state["hangover"]:
            print("Однако ваше состояние после пира оставляет желать лучшего.")
            successful_combat = combat(enemy_strength=100)
        else:
            if character_state["dysmoral"]:
                successful_combat = combat(enemy_strength=200)
            else:
                successful_combat = combat(enemy_strength=70)

        # Если игрок выиграл сражение
        if successful_combat:
            print("Против всех ожиданий вы зарекомендовали себя в бою и принесли победу викингам!")
            character_state['gold'] += 100
            end_game("Вы получаете золото и становитесь викингом!")

        else:
            # Если игрок проиграл сражение, игра окончена
            end_game("К несчастью, сегодня не ваш день. Вы пали в бою...", good_ending=False)


    else:
        print("Вы отказываетесь присоединяться к битве и уплачиваете 5 золотых монет.")
        character_state["gold"] -= 5
        caravan_encounter()