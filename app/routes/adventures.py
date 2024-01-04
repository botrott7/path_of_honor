from http.client import HTTPException
from fastapi import FastAPI, Request, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum

from app.routes.character_state import get_character_state, reset_character_state
from logi.logs import logger

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
    try:
        session = request.session
        user_id = session.get("user_id")
        reset_character_state(user_id)
        message = "Каждое квестовое задание описывает событие или ситуацию, а затем предлагает вам выбор из нескольких ответов. Ваш выбор будет оказывать влияние на ход и исход игры."
        return templates.TemplateResponse("adventures/adventures_start.html", {
            "request": request,
            "message": message,
        })
    except Exception as e:
        logger.error(f"Возникла ошибка start: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get('/reset')
async def handle_reset(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        reset_character_state(user_id)
        start_adventure_url = "/adventures/start"
        return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': start_adventure_url})
    except Exception as e:
        logger.error(f"Возникла ошибка reset: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get('/adventures/first_choice')
async def handle_choice(request: Request):
    session = request.session
    user_id = session.get("user_id")
    try:
        if user_id:
            character_state = get_character_state(user_id=user_id)
            choice_text = "Пред тобой раскинулись три дороги, как путеводня звезда в средневековых летописях. Прошу, скажи мне, куда желаешь отправиться?"
            choices = [choice.value for choice in AdventureChoices]
            return templates.TemplateResponse("adventures/adventures_choice.html", {
                "request": request,
                "choice_text": choice_text,
                "character_state": character_state,
                "choices": enumerate(choices)
            })
        else:
            message = "Вы не вошли как пользователь с ID "
            return templates.TemplateResponse("welcome.html", {"request": request, "message": message, })
    except Exception as e:
        logger.error(f"Возникла ошибка first_choice: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post('/adventures/first_choice')
async def handle_choice_post(request: Request):
    try:
        form_data = await request.form()
        choice = form_data.get('choice')
        if choice in adventure_urls:
            adventure_url = adventure_urls[choice]
            return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': adventure_url})
        elif choice == AdventureChoices.city:
            city_adventure_url = "/adventures/end"
            return Response(status_code=status.HTTP_303_SEE_OTHER, headers={'Location': city_adventure_url})
        else:
            return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Возникла ошибка first_choice_post: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
