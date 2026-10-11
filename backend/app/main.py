from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.api.endpoints import router as api_router
from app.data.seeder import seed_database_if_empty

# Створення таблиць в БД
Base.metadata.create_all(bind=engine)

# Ініціалізація початкових даних
with SessionLocal() as db:
    seed_database_if_empty(db)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Платформа реінтеграції ветеранів «VeteranPath Lviv» — від демобілізації до цивільного життя",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Для зручності локального запуску та демо
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "project": "VeteranPath Lviv API",
        "status": "online",
        "ai_mode": settings.AI_MODE,
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
