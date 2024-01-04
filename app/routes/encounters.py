from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Response, Request, status
from enum import Enum
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from app.routes.character_state import get_character_state
from logi.logs import logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class PersonChoices(str, Enum):
    run = "Бежать"
    fight = "Сражаться"
    gold = 'Откупиться'


class ChoiceInput(BaseModel):
    choice: PersonChoices
    intro_text: str
    choice_text: str


forests_urls = {
    PersonChoices.run: "/adventures/first_choice",
    PersonChoices.fight: "/adventures/fight",
    PersonChoices.gold: "/adventures/gold",
}

rivers_urls = {
    PersonChoices.run: "/adventures/first_choice",
    PersonChoices.fight: "/adventures/fight",
    PersonChoices.gold: "/adventures/gold",
}


@router.get("/adventures/forest")
async def forest_adventure(request: Request):
    try:
        message = "Войдя в лес, вы ощущаете мрачную тишину. Внезапно, перед вами появляется разбойник!"
        choices = [choice.value for choice in PersonChoices]
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        return templates.TemplateResponse("adventures/adventures_choice.html", {
            "request": request,
            "choice_text": message,
            "character_state": character_state,
            "choices": enumerate(choices)
        })
    except Exception as e:
        logger.error(f"Произошла ошибка во время приключения в лесу: {e}")


@router.post('/adventures/forest')
async def forest_adventure_post(request: Request):
    try:
        form_data = await request.form()
        choice = form_data.get('choice')
        if choice in forests_urls:
            forest_urls = rivers_urls[choice]
            return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': forest_urls})
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке POST-запроса во время приключения в лесу: {e}")


@router.get("/adventures/river")
async def river_adventure(request: Request):
    try:
        message = ("Приближаясь к реке, очесаете глазами живописный пейзаж,"
                   "вселяющий восхищение в душу. Однако, ваш взгляд привлекает невероятная сцена: перед вами - группа викингов,"
                   "горячо и усердно готовящих свои драккары к плаванию")
        message += "Викинги вас заметили и предложили отправиться с ними, предлагая вам сделку"
        message += "Вы должны одолеть их воина или раслпатиться золотом!"
        choices = [choice.value for choice in PersonChoices]
        session = request.session
        user_id = session.get("user_id")

        character_state = get_character_state(user_id=user_id)

        return templates.TemplateResponse("adventures/adventures_choice.html", {
            "request": request,
            "choice_text": message,
            "character_state": character_state,
            "choices": enumerate(choices)
        })
    except Exception as e:
        logger.error(f"Произошла ошибка во время приключения у реки: {e}")


@router.post('/adventures/river')
async def river_adventure_post(request: Request):
    try:
        form_data = await request.form()
        choice = form_data.get('choice')
        if choice in rivers_urls:
            river_urls = rivers_urls[choice]
            return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': river_urls})
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке POST-запроса во время приключения у реки: {e}")


@router.get("/adventures/city")
async def city_adventure(request: Request):
    return RedirectResponse("/adventures/end", status_code=307)
