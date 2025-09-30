from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .database import Base, engine
from .routers import public, admin, enrich

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ID Number Reputation Tracker", version="1.0.0")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
	return templates.TemplateResponse("index.html", {"request": request})


app.include_router(public.router, prefix="/api", tags=["public"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(enrich.router, prefix="/api/admin", tags=["admin"])


@app.get("/numbers/{e164}", response_class=HTMLResponse)
async def number_detail_page(e164: str, request: Request):
	return templates.TemplateResponse("detail.html", {"request": request, "e164": e164})


@app.get("/health")
async def health():
	return {"ok": True}