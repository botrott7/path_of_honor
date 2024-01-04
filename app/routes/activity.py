from http.client import HTTPException
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Response, Request
from starlette.responses import RedirectResponse
from urllib.parse import urlparse

from logi.logs import logger
from app.routes.character_state import get_character_state
from app.routes.combat import combat_function

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/adventures/fight")
async def fight_adventure(request: Request, response: Response):
    session = request.session
    user_id = session.get("user_id")
    message, player_attack_info, enemy_attack_info = await combat_function(enemy_strength=60, user_id=user_id)
    character_state = get_character_state(user_id=user_id)
    referrer = request.headers.get("Referer")
    url_path = urlparse(referrer).path
    try:
        if player_attack_info and enemy_attack_info:
            logger.info(f"Пользователь с ID {user_id} совершил действие")
            return templates.TemplateResponse("adventures/adventures_fight.html",
                                              {"request": request,
                                               "message": message,
                                               "player_attack_info": player_attack_info,
                                               "enemy_attack_info": enemy_attack_info,
                                               "character_state": character_state,
                                               "continue_url": "/adventures/kinght" if "/adventures/forest" in url_path else "/adventures/vikings"})
        elif 'Поражение' in message and character_state['health'] <= 0:
            return RedirectResponse("/adventures/end", status_code=307)
        else:
            logger.warning(f"Пользователь с ID {user_id} получил ошибку в битве")
            response.status_code = 400
            return "Ошибка"
    except Exception as e:
        logger.error(f"Возникла ошибка во время битвы: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/adventures/end")
async def end_adventure(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        return templates.TemplateResponse("adventures/adventures_end.html",
                                          {"request": request, "character_state": character_state})
    except Exception as e:
        logger.error(f"Возникла ошибка end: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
