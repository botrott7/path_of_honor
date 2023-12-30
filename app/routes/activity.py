from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Response, Request
from app.routes.combat import combat_function
from starlette.responses import RedirectResponse
from app.routes.character_state import get_character_state
from app.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/adventures/fight")
async def fight_adventure(request: Request, response: Response):
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    message, player_attack_info, enemy_attack_info = combat_function(enemy_strength=60, user_id=user_id, db=db)
    character_state = get_character_state(user_id=user_id, db=db)
    try:
        if player_attack_info and enemy_attack_info:
            return templates.TemplateResponse("adventures_fight.html",
                                              {"request": request,
                                               "message": message,
                                               "player_attack_info": player_attack_info,
                                               "enemy_attack_info": enemy_attack_info,
                                               "character_state": character_state})
        elif 'Поражение' in message and character_state['health'] <= 0:
            return RedirectResponse("/adventures/end", status_code=307)
        else:
            response.status_code = 400
            return "Ошибка"
    finally:
        db.close()


@router.get("/adventures/end")
async def end_adventure(request: Request):
    return templates.TemplateResponse("adventures_end.html", {"request": request})