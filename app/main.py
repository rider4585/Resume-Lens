"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import jds, match, recommendations
from app.services.storage import ensure_storage_dirs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure storage dirs on startup. Run DB migrations separately: alembic upgrade head."""
    ensure_storage_dirs()
    yield


app = FastAPI(
    title="Resume & JD Matcher",
    description="Evaluate a candidate's resume against a job description and return a fit score with explanation.",
    version="0.1.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(match.router, prefix="/api", tags=["match"])
app.include_router(jds.router, prefix="/api", tags=["jds"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])

# Templates and static
BASE_DIR = Path(__file__).parent
templates_dir = BASE_DIR / "templates"
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
else:
    templates = None

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/health")
def health():
    """Readiness check."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Serve the match form (web UI)."""
    if templates is not None:
        return templates.TemplateResponse(request, "index.html")
    return _fallback_root_html()


def _fallback_root_html() -> HTMLResponse:
    """Simple HTML when templates dir is missing."""
    return HTMLResponse(
        content="""<!DOCTYPE html><html><body><h1>Resume & JD Matcher</h1>
        <p>API docs: <a href="/docs">/docs</a> | Health: <a href="/health">/health</a></p></body></html>"""
    )
