from fastapi import FastAPI, Request, HTTPException
from fastapi.security import HTTPBasic
from fastapi.responses import RedirectResponse
from app.routes import adventures, activity, encounters, kinght
from fastapi.templating import Jinja2Templates
from app.models import User
from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from app.routes.character_state import get_user_from_database

import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(adventures.router)
app.include_router(encounters.router)
app.include_router(activity.router)
app.include_router(kinght.router)

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
    db: Session = SessionLocal()
    try:
        if not user:
            message = "Добро пожаловать в Path of Honor!\nВы - молодой рыцарь в погоне за славой и приключениями в средневековом мире."
            return templates.TemplateResponse("welcome.html", {"request": request, "message": message})
        else:
            user_id = str(session.get("user_id"))
            users = db.query(User).filter(User.id == user_id).first()
            message = "Вы вошли как пользователь с ID " + str(user_id)
            return templates.TemplateResponse("welcome.html", {"request": request, "message": message, "users": users})
    finally:
        db.close()


@app.route("/create_user", methods=["GET", "POST"])
async def create_user(request: Request):
    if request.method == "GET":
        return templates.TemplateResponse("create_user.html", {"request": request})
    elif request.method == "POST":
        form = await request.form()
        name = form.get("name")
        password = form.get("password")
        db: Session = SessionLocal()
        existing_user = db.query(User).filter(User.name == name).first()
        if existing_user:
            return templates.TemplateResponse("create_user.html", {"request": request,
                                                                   "message": "Пользователь с таким именем уже существует"})
        user = User(name=name, password=password, health=100, max_hp=100, gold=5, fatigue=False, hangover=False,
                    dysmoral=False)
        db.add(user)
        db.commit()
        db.refresh(user)
        request.session["user_id"] = user.id
        return templates.TemplateResponse("authenticated.html", {'request': request, 'user': user})


@app.get("/login")
async def login(request: Request):
    if "user_id" in request.session:
        return RedirectResponse(url="/")

    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user_id", None)
    return RedirectResponse(url="/", status_code=303)


@app.post("/authenticate")
async def authenticate(request: Request):
    form_data = await request.form()
    name = form_data.get('name')
    password = form_data.get('password')
    if not name or not password:
        raise HTTPException(status_code=400, detail="Пожалуйста, заполните все поля")
    user = get_user_from_database(name)
    if user is not None and password == user.password:
        request.session["user_id"] = user.id

        return templates.TemplateResponse("authenticated.html", {"request": request, "user": user})
    else:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request.state.detail = exc.detail
    return templates.TemplateResponse("login.html", {"request": request})
