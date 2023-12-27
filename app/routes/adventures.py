from fastapi import FastAPI, Request, Response, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum
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


@router.get('/adventures/choice')
async def handle_choice(request: Request):
    choice_text = "Перед вами две дороги снова. Куда желаете теперь направиться?"
    choices = [choice.value for choice in AdventureChoices]

    return templates.TemplateResponse("choice.html", {
        "request": request,
        "choice_text": choice_text,
        "choices": enumerate(choices)
    })


@router.post('/adventures/choice')
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
