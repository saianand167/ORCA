from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.location import get_all_locations, get_location
from .database.database import init_db
from .api.chat import router as chat_router
from .api.weather import router as weather_router
from .api.ocean import router as ocean_router
from .api.pfz import router as pfz_router
from .api.warnings import router as warnings_router
from .api.map import router as map_router
from .api.sources import router as sources_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Conversational Marine Intelligence Platform with Collaborative Agents (ISRO SIH26176)"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ORCA Marine Intelligence API",
        "version": settings.VERSION
    }

@app.get("/api/location")
def list_locations():
    return get_all_locations()

@app.get("/api/location/{loc_id}")
def retrieve_location(loc_id: str):
    return get_location(loc_id)

# Register API Routers
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(weather_router, prefix=settings.API_V1_PREFIX)
app.include_router(ocean_router, prefix=settings.API_V1_PREFIX)
app.include_router(pfz_router, prefix=settings.API_V1_PREFIX)
app.include_router(warnings_router, prefix=settings.API_V1_PREFIX)
app.include_router(map_router, prefix=settings.API_V1_PREFIX)
app.include_router(sources_router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
