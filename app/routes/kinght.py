from http.client import HTTPException
from starlette.responses import RedirectResponse
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Response, Request, status
from enum import Enum
from pydantic import BaseModel

from app.routes.combat import combat_function
from app.routes.character_state import get_character_state, update_character_state
from logi.logs import logger

router = APIRouter()
templates = Jinja2Templates(directory="templates")


class ForestChoices(str, Enum):
    sleep = "Переночевать"
    move = "Двигаться дальше"


class KinghtChoices(str, Enum):
    war = "Присоединиться к армии"
    refuse = "Отказаться"


class KinghtInput(BaseModel):
    choice: ForestChoices
    intro_text: str
    choice_text: str


kinghts_urls = {
    ForestChoices.sleep: "/adventures/camp",
    KinghtChoices.war: "/adventures/war",
    KinghtChoices.refuse: "/adventures/caravan"
}


@router.get("/adventures/kinght")
async def kinght_adventure(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        message = "Желаете переночевать в лесу или рискнуть и двинуться дальше?"
        choices = [choice.value for choice in ForestChoices]
        return templates.TemplateResponse("adventures/adventures_kinght.html", {
            "request": request,
            "choice_text": message,
            "choices": enumerate(choices),
            "character_state": character_state
        })
    except Exception as e:
        logger.error('Ошибка ветка про короля', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post('/adventures/kinght')
async def kinght_adventure_post(request: Request):
    session = request.session
    user_id = session.get("user_id")
    character_state = get_character_state(user_id=user_id)
    logger.debug('kinght_adventure_post %s', character_state)
    logger.debug('character_state["health"] %s', character_state["health"])
    form_data = await request.form()
    choice = form_data.get('choice')
    try:
        if choice == ForestChoices.sleep:
            character_state["health"] = min(character_state["health"] + 20, character_state["max_hp"])
            update_character_state(user_id, character_state)
            return RedirectResponse(kinghts_urls[ForestChoices.sleep], status_code=status.HTTP_303_SEE_OTHER)
        elif choice == ForestChoices.move:
            character_state['fatigue'] = True
            update_character_state(user_id, character_state)
            return RedirectResponse(kinghts_urls[ForestChoices.sleep], status_code=status.HTTP_303_SEE_OTHER)
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error('Ошибка в POST-запросе ветка про короля', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get('/adventures/camp')
async def camp_adventure_get(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        message = ("Вы прибыли в лагерь, где местный военачальник собирает армию для борьбы с викингами."
                   "Присоединитесь к армии и поможете защитить земли от викингов или откажетесь?")
        choices = [choice.value for choice in KinghtChoices]
        return templates.TemplateResponse("adventures/adventures_kinght.html", {
            "request": request,
            "choice_text": message,
            "choices": enumerate(choices),
            "character_state": character_state
        })
    except Exception as e:
        logger.error('Ошибка ветка camp', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post('/adventures/camp')
async def camp_adventure_post(request: Request):
    try:
        form_data = await request.form()
        choice = form_data.get('choice')
        if choice == KinghtChoices.war:
            return RedirectResponse(kinghts_urls[KinghtChoices.war], status_code=status.HTTP_303_SEE_OTHER)
        elif choice == KinghtChoices.refuse:
            return RedirectResponse(kinghts_urls[KinghtChoices.refuse], status_code=status.HTTP_303_SEE_OTHER)
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error('Ошибка в POST-запросе ветка camp', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get('/adventures/war')
async def war_adventure(request: Request, response: Response):
    try:
        session = request.session
        user_id = session.get("user_id")
        await combat_function(enemy_strength=60, user_id=user_id)
        logger.debug('WAR, combat_function', combat_function)
        return RedirectResponse("/adventures/end", status_code=307)
    except Exception as e:
        logger.error('Ошибка в war', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
