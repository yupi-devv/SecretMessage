from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from src.endpoints import rtr

app = FastAPI(
    docs_url="/docs",
    redoc_url=None,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(rtr)

templates = Jinja2Templates(directory="templates")


# Главная страница - создание сообщения
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_url": "/v1", "mode": "create", "code": None},
    )


# Просмотр сообщения по коду - /{code}
@app.get("/{code}")
async def view_message_by_code(request: Request, code: str):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"api_url": "/v1", "mode": "view", "code": code},
    )
