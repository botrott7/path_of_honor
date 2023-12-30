from starlette.responses import RedirectResponse
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Response, Request, status
from enum import Enum
from pydantic import BaseModel
from app.routes.combat import combat_function
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.routes.character_state import get_character_state, update_character_state

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
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    character_state = get_character_state(user_id=user_id, db=db)
    message = "Желаете переночевать в лесу или рискнуть и двинуться дальше?"

    choices = [choice.value for choice in ForestChoices]

    return templates.TemplateResponse("adventures_kinght.html", {
        "request": request,
        "choice_text": message,
        "choices": enumerate(choices),
        "character_state": character_state
    })


@router.post('/adventures/kinght')
async def kinght_adventure_post(request: Request):
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    character_state = get_character_state(user_id=user_id, db=db)
    print('kinght_adventure_post', character_state)
    print('character_state["health"]', character_state["health"])
    form_data = await request.form()
    choice = form_data.get('choice')

    try:
        if choice == ForestChoices.sleep:
            character_state["health"] = min(character_state["health"] + 20, character_state["max_hp"])
            update_character_state(user_id, db, character_state)
            return RedirectResponse(kinghts_urls[ForestChoices.sleep], status_code=status.HTTP_303_SEE_OTHER)

        elif choice == ForestChoices.move:
            character_state['fatigue'] = True
            update_character_state(user_id, db, character_state)
            return RedirectResponse(kinghts_urls[ForestChoices.sleep], status_code=status.HTTP_303_SEE_OTHER)
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    finally:
        db.close()
@router.get('/adventures/camp')
async def camp_adventure_get(request: Request):
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    character_state = get_character_state(user_id=user_id, db=db)

    message = ("Вы прибыли в лагерь, где местный военачальник собирает армию для борьбы с викингами."
               "Присоединитесь к армии и поможете защитить земли от викингов или откажетесь?")

    choices = [choice.value for choice in KinghtChoices]

    return templates.TemplateResponse("adventures_kinght.html", {
        "request": request,
        "choice_text": message,
        "choices": enumerate(choices),
        "character_state": character_state
    })

@router.post('/adventures/camp')
async def camp_adventure_post(request: Request):
    form_data = await request.form()
    choice = form_data.get('choice')

    if choice == KinghtChoices.war:
        return RedirectResponse(kinghts_urls[KinghtChoices.war], status_code=status.HTTP_303_SEE_OTHER)
    elif choice == KinghtChoices.refuse:
        return RedirectResponse(kinghts_urls[KinghtChoices.refuse], status_code=status.HTTP_303_SEE_OTHER)
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

@router.get('/adventures/war')
async def war_adventure(request: Request, response: Response):
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    message, player_attack_info, enemy_attack_info = combat_function(enemy_strength=60, user_id=user_id, db=db)
    character_state = get_character_state(user_id=user_id, db=db)
    if player_attack_info and enemy_attack_info:
        message = 'Ваша храбрость и мастерство помогли победить викингов! Вы становитесь героем сражения.'
        return templates.TemplateResponse("adventures_kinght_final.html",
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