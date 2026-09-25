import logging
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from config import AI_BASE_URL, AI_MODEL, GEMINI_API_KEY
from models.schemas import Resume, load_resume

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """You answer recruiter questions using only the supplied resume context.

Rules:
- Use only information contained in the provided resume.
- Never invent employment dates, skills, companies, education, projects, responsibilities, or experience.
- If the resume does not contain enough information, explicitly say: The resume does not provide enough information to answer this confidently.
- Do not assume that a technology mentioned in a project means professional production experience unless the resume explicitly says so.
- Distinguish documented facts from uncertainty.
- Identify employment gaps only by comparing documented employment dates. Do not invent an explanation for a gap.
- Do not hide ambiguous or missing information.
- Keep answers concise but useful for a recruiter.

Return only the answer text, without JSON or markdown wrappers."""

RESUME_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_resume.json"


class MissingAPIKeyError(RuntimeError):
	"""Raised when the configured LLM API key is unavailable."""


class ResumeQuestionError(RuntimeError):
	"""Raised when the LLM cannot answer a resume question."""


def _redact_provider_message(message: str) -> str:
	"""Remove the configured API key before writing provider errors to logs."""
	if GEMINI_API_KEY:
		return message.replace(GEMINI_API_KEY, "[REDACTED_API_KEY]")
	return message


def build_resume_context(resume: Resume) -> str:
	"""Serialize only the validated resume fields used by the LLM."""
	return resume.model_dump_json(indent=2)


def answer_resume_question(question: str) -> tuple[str, bool]:
	"""Answer a recruiter question with a response grounded in the mock resume."""
	if not question.strip():
		raise ValueError("Question must not be empty.")

	resume = load_resume(RESUME_PATH)
	if not GEMINI_API_KEY:
		raise MissingAPIKeyError("GEMINI_API_KEY is not configured.")

	client = OpenAI(api_key=GEMINI_API_KEY, base_url=AI_BASE_URL)
	try:
		response = client.chat.completions.create(
			model=AI_MODEL,
			messages=[
				{
					"role": "system",
					"content": SYSTEM_PROMPT,
				},
				{
					"role": "user",
					"content": (
						"Resume context:\n"
						f"{build_resume_context(resume)}\n\n"
						f"Recruiter question: {question.strip()}"
					),
				},
			],
		)
	except Exception as error:
		status_code = getattr(error, "status_code", None)
		logger.error(
			"Gemini provider request failed: exception_type=%s status_code=%s message=%s",
			type(error).__name__,
			status_code if status_code is not None else "unavailable",
			_redact_provider_message(str(error)),
		)
		if status_code == 429:
			raise ResumeQuestionError(
				"AI service quota is temporarily exhausted. Please try again later."
			) from error
		raise ResumeQuestionError("The resume question could not be answered.") from error

	answer = (response.choices[0].message.content or "").strip()
	if not answer:
		raise ResumeQuestionError("The resume question returned an empty answer.")

	grounded = "not provide enough information" not in answer.lower()
	return answer, grounded
