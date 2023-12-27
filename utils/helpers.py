
def make_choice(prompt: str, options: list):
    """Вывод сценариев и запросов игрока,
    принимает promt = предложение или вопрос, выводимый для игрока,
    принимает options = списко опций или вариантов ответов"""
    print(prompt)
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    choice = input("Выберите действие: ")
    print("=" * 100)
    while not choice.isdigit() or not (0 < int(choice) <= len(options)):
        choice = input("Пожалуйста, сделайте ваш выбор цифрами, которые соответствуют опциям: ")
    return int(choice)
