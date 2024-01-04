import os

from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBasic
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from app.routes.character_state import get_user_from_database

from logi.logs import logger
from app.routes import (auth, adventures, activity, encounters,
                        kinght, caravan, gold, vikings)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)
app.include_router(adventures.router)
app.include_router(encounters.router)
app.include_router(activity.router)
app.include_router(gold.router)
app.include_router(kinght.router)
app.include_router(caravan.router)
app.include_router(vikings.router)

secret_key = os.urandom(100 // 8)
app.add_middleware(SessionMiddleware, secret_key=secret_key)

security = HTTPBasic()


class UserCredentials(BaseModel):
    name: str
    password: str


@app.get("/")
async def root(request: Request):
    session = request.session
    user = session.get("user_id")
    try:
        if not user:
            message = "Добро пожаловать в Path of Honor! В игре вы воплощаете роль молодого рыцаря, стремящегося к славе и приключениям. Ваше первое задание - выбрать своего персонажа и дать ему имя."
            return templates.TemplateResponse("welcome.html", {"request": request, "message": message})
        else:
            user_id = str(session.get("user_id"))
            users = get_user_from_database(user_id)
            message = "Вы вошли как пользователь с ID " + str(user_id)
            return templates.TemplateResponse("welcome.html", {"request": request, "message": message, "users": users})
    except Exception as e:
        logger.error(f'Ошибка: {str(e)}')
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request.state.detail = exc.detail
    return templates.TemplateResponse("login.html", {"request": request})
