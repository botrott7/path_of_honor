from fastapi import FastAPI, Request
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from app.routes.character_state import get_character_state, update_character_state


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
        return templates.TemplateResponse("adventures_gold.html",
                                          {"request": request,
                                           "message": message,
                                           "character_state": character_state})
    finally:
        pass



