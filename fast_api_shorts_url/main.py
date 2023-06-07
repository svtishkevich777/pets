from fastapi import FastAPI
import models
from database import engine, Base
from routers import auth, shorts
from starlette.staticfiles import StaticFiles
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/shorts/", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(shorts.router)
