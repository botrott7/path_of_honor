from fastapi import FastAPI, Request
from app.routes import adventures, combat, encounters
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

app.include_router(adventures.router)
app.include_router(encounters.router)


@app.get('/')
async def handle_get_request(request: Request):
    message = "Добро пожаловать в Path of Honor!\nВы - молодой рыцарь в погоне за славой и приключениями в средневековом мире."
    return templates.TemplateResponse("index.html", {"request": request, "message": message})
