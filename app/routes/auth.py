from fastapi import Request, APIRouter, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic
from pydantic import BaseModel

from logi.logs import logger
from .character_state import get_user_from_database, create_new_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

security = HTTPBasic()


class UserCredentials(BaseModel):
    name: str
    password: str


@router.get("/login")
async def login(request: Request):
    try:
        if "user_id" in request.session:
            return RedirectResponse(url="/")
        return templates.TemplateResponse("login.html", {"request": request})
    except Exception as e:
        logger.error(f"Возникла ошибка login: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.get("/logout")
async def logout(request: Request):
    try:
        request.session.pop("user_id", None)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        logger.error(f"Возникла ошибка logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@router.post("/authenticate")
async def authenticate(request: Request):
    try:
        form_data = await request.form()
        name = form_data.get('name')
        password = form_data.get('password')
        if not name or not password:
            raise HTTPException(status_code=400, detail="Пожалуйста, заполните все поля")
        user = get_user_from_database(name)
        if user is not None and password == user.password:
            request.session["user_id"] = user.id
            return templates.TemplateResponse("adventures/authenticated.html", {"request": request, "user": user})
        else:
            raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")
    except Exception as e:
        logger.error(f"Возникла ошибка authenticate: {str(e)}")
        raise HTTPException(status_code=500, detail="Неверное имя пользователя или пароль")


@router.route("/create_user", methods=["GET", "POST"])
async def create_user(request: Request):
    try:
        if request.method == "GET":
            return templates.TemplateResponse("create_user.html", {"request": request})
        elif request.method == "POST":
            form = await request.form()
            name = form.get("name")
            password = form.get("password")
            existing_user = get_user_from_database(name)
            if existing_user:
                return templates.TemplateResponse("create_user.html", {"request": request,
                                                                       "message": "Пользователь с таким именем уже существует"})
            user = create_new_user(name=name, password=password)
            request.session["user_id"] = user.id
            return templates.TemplateResponse("authenticated.html", {'request': request, 'user': user})
    except Exception as e:
        logger.error(f"Возникла ошибка create_user: {str(e)}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
