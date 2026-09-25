import os

from dotenv import load_dotenv

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gemini-3.8-flash")
AI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
