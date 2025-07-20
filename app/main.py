from fastapi import FastAPI

from app.core.logging import configure_logging, RequestIdMiddleware
from app.core.metrics import MetricsMiddleware, metrics_endpoint
from app.api import (
    auth,
    templates,
    taxonomy,
    generation,
    generation_jobs,
    fields,
    lookups,
    search,
    template_versions,
    audit,
    users,
)
from app.models import Base
from app.core.db import engine

configure_logging()

app = FastAPI(title="Document Generator")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(MetricsMiddleware)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
app.include_router(taxonomy.router, prefix="/api/taxonomy", tags=["taxonomy"])
app.include_router(generation.router, prefix="/api/generate", tags=["generation"])
app.include_router(generation_jobs.router, prefix="/api/generation-jobs", tags=["generation_jobs"])
app.include_router(fields.router, prefix="/api/fields", tags=["fields"])
app.include_router(lookups.router, prefix="/api/lookups", tags=["lookups"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(
    template_versions.router, prefix="/api", tags=["template_versions"]
)
app.include_router(audit.router, prefix="/api/audit", tags=["audit"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], tags=["metrics"])


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"status": "ok"}
