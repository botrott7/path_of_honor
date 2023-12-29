from fastapi import FastAPI, Request, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.routes.character_state import get_character_state, reset_character_state

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


class AdventureChoices(str, Enum):
    forest = "Лес"
    river = "Река"
    city = 'Город'


class ChoiceInput(BaseModel):
    choice: AdventureChoices
    intro_text: str
    choice_text: str


adventure_urls = {
    AdventureChoices.forest: "/adventures/forest",
    AdventureChoices.river: "/adventures/river",
}


@router.get('/adventures/start')
async def handle_choice(request: Request):
    message = "Это квест игра где вам предстоит делать выбор"
    return templates.TemplateResponse("adventures_start.html", {
        "request": request,
        "message": message,
    })


@router.get('/reset')
async def handle_reset(request: Request):
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    reset_character_state(user_id, db)
    start_adventure_url = "/adventures/start"
    return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': start_adventure_url})


@router.get('/adventures/first_choice')
async def handle_choice(request: Request):
    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    try:
        if user_id:
            character_state = get_character_state(user_id=user_id, db=db)
            choice_text = "Перед вами две дороги снова. Куда желаете теперь направиться?"
            choices = [choice.value for choice in AdventureChoices]

            return templates.TemplateResponse("adventures_choice.html", {
                "request": request,
                "choice_text": choice_text,
                "character_state": character_state,
                "choices": enumerate(choices)
            })
        else:
            message = "Вы не вошли как пользователь с ID "
            return templates.TemplateResponse("welcome.html", {"request": request, "message": message, })
    finally:
        db.close()


@router.post('/adventures/first_choice')
async def handle_choice_post(request: Request):
    form_data = await request.form()
    choice = form_data.get('choice')
    if choice in adventure_urls:
        adventure_url = adventure_urls[choice]
        return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': adventure_url})
    elif choice == AdventureChoices.city:
        city_adventure_url = "/adventures/city"
        return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': city_adventure_url})
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
