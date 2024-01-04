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


class RiverChoices(str, Enum):
    beer = "Учавствовать"
    observe = "Наблюдать"


class KinghtChoices(str, Enum):
    war = "Присоединиться к армии"
    refuse = "Отказаться"


class KinghtInput(BaseModel):
    choice: RiverChoices
    intro_text: str
    choice_text: str


kinghts_urls = {
    RiverChoices.beer: "/adventures/vik_camp",
    KinghtChoices.war: "/adventures/vik_war",
    KinghtChoices.refuse: "/adventures/caravan"
}


@router.get("/adventures/vikings")
async def vikings_adventure(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        message = "Викинги на корабле предлагают соревнование: кто выпьет больше пива!"
        choices = [choice.value for choice in RiverChoices]
        return templates.TemplateResponse("adventures/adventures_kinght.html", {
            "request": request,
            "choice_text": message,
            "choices": enumerate(choices),
            "character_state": character_state
        })
    except Exception as e:
        logger.error('Ошибка ветка про викингов', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post('/adventures/vikings')
async def vikings_adventure_post(request: Request):
    session = request.session
    user_id = session.get("user_id")
    character_state = get_character_state(user_id=user_id)
    form_data = await request.form()
    choice = form_data.get('choice')
    try:
        if choice == RiverChoices.observe:
            character_state["health"] = min(character_state["health"] + 20, character_state["max_hp"])
            update_character_state(user_id, character_state)
            return RedirectResponse(kinghts_urls[RiverChoices.beer], status_code=status.HTTP_303_SEE_OTHER)
        elif choice == RiverChoices.beer:
            character_state['hangover'] = True
            update_character_state(user_id, character_state)
            return RedirectResponse(kinghts_urls[RiverChoices.beer], status_code=status.HTTP_303_SEE_OTHER)
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error('Ошибка в POST-запросе ветка про викингов', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get('/adventures/vik_camp')
async def vik_camp_adventure_get(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        message = ("Во главе корабля стоит величественный викинг и задаёт вам вопрос:"
                   "Готовы ли вы присоединиться к их стороне в предстоящей битве?")
        choices = [choice.value for choice in KinghtChoices]
        return templates.TemplateResponse("adventures/adventures_kinght.html", {
            "request": request,
            "choice_text": message,
            "choices": enumerate(choices),
            "character_state": character_state
        })
    except Exception as e:
        logger.error('Ошибка ветка vik_camp', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post('/adventures/vik_camp')
async def vik_camp_adventure_post(request: Request):
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
        logger.error('Ошибка в POST-запросе ветка vik_camp', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get('/adventures/vik_war')
async def vik_war_adventure(request: Request, response: Response):
    try:
        session = request.session
        user_id = session.get("user_id")
        await combat_function(enemy_strength=60, user_id=user_id)
        logger.debug('WAR, combat_function', combat_function)
        return RedirectResponse("/adventures/end", status_code=307)
    except Exception as e:
        logger.error('Ошибка в vik_war', str(e))
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
