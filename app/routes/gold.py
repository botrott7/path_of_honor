from fastapi import FastAPI, Request, Response, status, Depends
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.routes.character_state import get_character_state, reset_character_state
from app.routes.character_state import get_character_state, update_character_state
from starlette.responses import RedirectResponse


app = FastAPI()
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/adventures/gold')
async def gold_adventure(request: Request):

    session = request.session
    user_id = session.get("user_id")
    db: Session = SessionLocal()
    character_state = get_character_state(user_id=user_id, db=db)

    try:
        character_state['gold'] -= 5
        await update_character_state(user_id, db, character_state)
        message = 'Вы потеряли всё свое золото'
        return templates.TemplateResponse("adventures_gold.html",
                                          {"request": request,
                                           "message": message,
                                           "character_state": character_state})
    finally:
        db.close()



