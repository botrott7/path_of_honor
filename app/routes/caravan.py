from fastapi import FastAPI, Request, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum

from app.routes.character_state import get_character_state
from starlette.responses import RedirectResponse
from logi.logs import logger

app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


class CaravanChoices(str, Enum):
    caravan = "Согласиться"
    wanderer = "Отказаться"


class ChoiceInput(BaseModel):
    choice: CaravanChoices
    intro_text: str
    choice_text: str


caravan_urls = {
    CaravanChoices.caravan: "/adventures/end",
    CaravanChoices.wanderer: "/adventures/end",
}


@router.route('/adventures/caravan', methods=['GET', 'POST'])
async def gold_adventure(request: Request):
    try:
        session = request.session
        user_id = session.get("user_id")
        character_state = get_character_state(user_id=user_id)
        message = ("На пути вы встречаете караван торговцев. Они готовятся к дальнему путешествию через пустыню."
                   "Торговцы предлагают присоединиться к ним, но у вас должен быть начальный капитал")
        choices = [choice.value for choice in CaravanChoices]
        if request.method == 'GET':
            logger.debug("Получен GET-запрос")
            return templates.TemplateResponse("adventures/adventures_caravan.html", {
                "request": request,
                "message": message,
                "choices": enumerate(choices),
                "character_state": character_state
            })
        elif request.method == 'POST':
            logger.debug("Получен POST-запрос")
            form_data = await request.form()
            choice = form_data.get('choice')
            if choice == CaravanChoices.caravan:
                if character_state['gold'] >= 10:
                    logger.info(f"Выбрана опция Caravan и у персонажа достаточно золота: {character_state['gold']}")
                    return RedirectResponse(caravan_urls[CaravanChoices.caravan], status_code=status.HTTP_303_SEE_OTHER)
                else:
                    message = 'У вас недостаточно золота'
                    return templates.TemplateResponse("adventures/adventures_end.html", {"request": request, "message": message})
            elif choice == CaravanChoices.wanderer:
                return RedirectResponse(caravan_urls[CaravanChoices.wanderer], status_code=status.HTTP_303_SEE_OTHER)
            else:
                logger.warning("Выбрана некорректная опция")
                return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
