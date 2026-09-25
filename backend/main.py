from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import FRONTEND_URL
from routes.query import router as query_router
from routes.resume import router as resume_router

app = FastAPI(title="HireFlow AI Backend")

app.add_middleware(
	CORSMiddleware,
	allow_origins=[FRONTEND_URL, "http://127.0.0.1:5174", "http://localhost:5174", "http://localhost:5173", "http://127.0.0.1:5173"] ,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(resume_router, prefix="/api/resume")
app.include_router(query_router, prefix="/api/resume")


@app.get("/api/health")
def health_check() -> dict[str, str]:
	return {
		"status": "ok",
		"service": "hireflow-ai-backend",
	}
