from urllib.parse import urlparse
from fastapi import FastAPI, Request
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from app.routes.character_state import get_character_state, update_character_state
from logi.logs import logger

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/adventures/gold')
async def gold_adventure(request: Request):
    session = request.session
    user_id = session.get("user_id")
    character_state = get_character_state(user_id=user_id)
    try:
        character_state['gold'] -= 5
        update_character_state(user_id, character_state)
        message = 'Вы потеряли всё свое золото'
        referrer = request.headers.get("Referer")
        url_path = urlparse(referrer).path
        return templates.TemplateResponse("adventures/adventures_gold.html",
                                          {"request": request,
                                           "message": message,
                                           "character_state": character_state,
                                           "continue_url": "/adventures/kinght" if "/adventures/forest" in url_path else "/adventures/vikings"})
    except Exception as e:
        logger.error(f"Произошла ошибка во время выбора gold: {e}")
