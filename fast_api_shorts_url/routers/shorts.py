import sys
sys.path.append("..")

from fastapi import Depends, APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette import status
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, SessionLocal
import models
from datetime import datetime
from .auth import get_current_user
from random import choices
import string


CHARACTERS = string.digits + string.ascii_letters
key = 4


router = APIRouter(
    prefix="/shorts",
    tags=["shorts"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def generate_random_short_url(db):
    new_short_not_repeat = ''
    while True:
        generate_short = ''.join(choices(CHARACTERS, k=key))
        new_short_not_repeat += generate_short
        check = db.query(models.Shorts).filter(models.Shorts.short_url == new_short_not_repeat).first()
        if check is None:
            break
    return new_short_not_repeat


class Shorts(BaseModel):
    origin_url: str
    short_url: str
    visits: int
    date_create: datetime


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    shorts = db.query(models.Shorts).filter(models.Shorts.owner_id == user.get("id")).all()

    host = request.url._url

    return templates.TemplateResponse("home.html", {"request": request, "shorts": shorts, "user": user, "host": host})


@router.get("/add-short", response_class=HTMLResponse)
async def form_for_filling(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("create_short.html", {"request": request, "user": user})


@router.post("/add-short", response_class=HTMLResponse)
async def create_short_url(request: Request, origin_url: str = Form(default=None), short_url: str = Form(max_length=4, default="generate_short"), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if origin_url is None:
        messages = 'Please enter your Url!'
        return templates.TemplateResponse("create_short.html", {"request": request,
                                                                "user": user,
                                                                "messages": messages})

    if short_url == "generate_short":
        short_url = generate_random_short_url(db)

    check = db.query(models.Shorts).filter(models.Shorts.short_url == short_url).first()
    if check:
        messages = f'Such a short url already exists -> {short_url}'
        return templates.TemplateResponse("create_short.html", {"request": request,
                                                                "user": user,
                                                                "messages": messages,
                                                                "origin_url": origin_url})

    short_model = models.Shorts()
    short_model.origin_url = origin_url
    short_model.short_url = short_url
    short_model.owner_id = user.get("id")

    db.add(short_model)
    db.commit()

    return RedirectResponse(url="/shorts", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{short_id}", response_class=HTMLResponse)
async def delete_short(request: Request, short_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    short_model = db.query(models.Shorts)\
        .filter(models.Shorts.id == short_id) \
        .filter(models.Shorts.owner_id == user.get("id"))\
        .first()

    if short_model is None:
        return RedirectResponse(url="/shorts", status_code=status.HTTP_302_FOUND)

    db.query(models.Shorts).filter(models.Shorts.id == short_id).delete()

    db.commit()

    return RedirectResponse(url="/shorts", status_code=status.HTTP_302_FOUND)


@router.get("/{short_url}")
async def redirect_url(request: Request, short_url: str, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    short_visit = db.query(models.Shorts).filter(models.Shorts.short_url == short_url).first()

    if short_visit is None:
        return RedirectResponse(url="/shorts", status_code=status.HTTP_302_FOUND)

    short_visit.visits += 1

    db.add(short_visit)
    db.commit()

    return RedirectResponse(url=short_visit.origin_url, status_code=status.HTTP_302_FOUND)
