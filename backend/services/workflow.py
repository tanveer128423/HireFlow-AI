import json
import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI
from pydantic import ValidationError

from config import AI_BASE_URL, AI_MODEL, GEMINI_API_KEY
from models.schemas import HREvaluation, Resume, load_resume

logger = logging.getLogger(__name__)

RESUME_PATH = Path(__file__).resolve().parents[1] / "data" / "mock_resume.json"

WORKFLOW_SYSTEM_PROMPT = """You generate a structured Corporate Hiring Evaluation Form from the supplied resume.

Grounding rules:
- Use only documented information in the resume and the calculated employment dates supplied in context.
- Never invent dates, skills, companies, education, projects, responsibilities, experience, or management history.
- Do not treat a project technology as professional production experience unless the resume explicitly documents that experience.
- Distinguish documented facts from cautious inferences. Do not present inferences as facts.
- Employment gaps must use only the documented employment dates. Do not add an explanation for any gap.
- For unavailable information, use null, an empty array, or "Not specified in resume" as appropriate.
- Do not claim team management because the resume does not document it.
- Potential concerns may contain only documented employment gaps or explicitly unavailable information.
- Do not infer seniority, performance, corporate-team experience, or total experience beyond the documented dates.
- Any recommendation must be clearly framed as an inference from documented job titles and technologies.
- Keep the evaluation concise and recruiter-useful.

Return only valid JSON with exactly these fields:
candidate_name, email, primary_skillset, years_of_experience, education,
employment_summary, employment_gaps, key_projects, cloud_experience,
technical_strengths, potential_concerns, recommended_role,
recommendation_reason, generated_at, status.

Set status to "completed". Set generated_at to the supplied generation timestamp.
"""


class WorkflowError(RuntimeError):
	"""Base error for evaluation workflow failures."""


class MissingWorkflowAPIKeyError(WorkflowError):
	"""Raised when Gemini credentials are unavailable."""


class EvaluationGenerationError(WorkflowError):
	"""Raised when Gemini output cannot become a valid evaluation."""


def _month_start(value: str) -> date:
	year, month = (int(part) for part in value.split("-", 1))
	return date(year, month, 1)


def _next_month(value: date) -> date:
	if value.month == 12:
		return date(value.year + 1, 1, 1)
	return date(value.year, value.month + 1, 1)


def _previous_month(value: date) -> date:
	if value.month == 1:
		return date(value.year - 1, 12, 1)
	return date(value.year, value.month - 1, 1)


def calculate_employment_gaps(resume: Resume) -> list[str]:
	"""Calculate gaps between adjacent documented employment periods."""
	employment = sorted(resume.employment_history, key=lambda item: item.start)
	gaps: list[str] = []
	for previous, current in zip(employment, employment[1:]):
		gap_start = _next_month(_month_start(previous.end))
		gap_end = _previous_month(_month_start(current.start))
		if gap_start <= gap_end:
			gaps.append(f"{gap_start:%Y-%m} to {gap_end:%Y-%m}")
	return gaps


def build_evaluation_context(resume: Resume, generated_at: str) -> str:
	"""Build controlled resume context with dates calculated from documented jobs."""
	context: dict[str, Any] = resume.model_dump()
	context["calculated_employment_gaps"] = calculate_employment_gaps(resume)
	context["generation_timestamp"] = generated_at
	return json.dumps(context, indent=2)


def _extract_json(text: str) -> dict[str, Any]:
	cleaned = text.strip()
	if cleaned.startswith("```"):
		lines = cleaned.splitlines()
		cleaned = "\n".join(lines[1:-1])
	try:
		payload = json.loads(cleaned)
	except json.JSONDecodeError as error:
		raise EvaluationGenerationError(
			"Gemini returned an evaluation that was not valid JSON."
		) from error
	if not isinstance(payload, dict):
		raise EvaluationGenerationError("Gemini evaluation must be a JSON object.")
	return payload


def _stringify(value: Any) -> str:
	if isinstance(value, str):
		return value
	if isinstance(value, (dict, list)):
		return json.dumps(value, ensure_ascii=True)
	return str(value)


def _project_strings(value: Any) -> list[str]:
	if not isinstance(value, list):
		return []
	projects: list[str] = []
	for project in value:
		if isinstance(project, dict):
			name = project.get("name", "Project")
			description = project.get("description", "Not specified in resume")
			technologies = project.get("technologies", [])
			projects.append(
				f"{name}: {description} Technologies: "
				f"{', '.join(_stringify(item) for item in technologies)}"
			)
		else:
			projects.append(_stringify(project))
	return projects


def _strength_strings(value: Any) -> list[str]:
	if isinstance(value, list):
		return [_stringify(item) for item in value]
	if isinstance(value, dict):
		return [
			f"{key}: {', '.join(_stringify(item) for item in items) if isinstance(items, list) else _stringify(items)}"
			for key, items in value.items()
		]
	return []


def _documented_experience_years(resume: Resume) -> float:
	months: set[tuple[int, int]] = set()
	for employment in resume.employment_history:
		start = _month_start(employment.start)
		end = _month_start(employment.end)
		while start <= end:
			months.add((start.year, start.month))
			start = _next_month(start)
	return round(len(months) / 12, 2)


def _normalize_evaluation_payload(
	payload: dict[str, Any], resume: Resume, generated_at: str
) -> dict[str, Any]:
	"""Normalize Gemini's JSON shapes without adding resume facts."""
	if not isinstance(payload.get("years_of_experience"), (int, float)):
		payload["years_of_experience"] = _documented_experience_years(resume)
	if not isinstance(payload.get("education"), str):
		payload["education"] = _stringify(payload.get("education", "Not specified in resume"))
	if not isinstance(payload.get("employment_summary"), str):
		payload["employment_summary"] = _stringify(
			payload.get("employment_summary", "Not specified in resume")
		)
	payload["key_projects"] = _project_strings(payload.get("key_projects", []))
	if not isinstance(payload.get("cloud_experience"), str):
		payload["cloud_experience"] = _stringify(
			payload.get("cloud_experience", "Not specified in resume")
		)
	payload["technical_strengths"] = _strength_strings(
		payload.get("technical_strengths", [])
	)
	employment_gaps = calculate_employment_gaps(resume)
	payload["employment_gaps"] = employment_gaps
	payload["potential_concerns"] = [
		f"Documented employment gap: {gap}" for gap in employment_gaps
	]
	payload["candidate_name"] = resume.candidate.name
	payload["email"] = resume.candidate.email
	payload["generated_at"] = generated_at
	payload["status"] = "completed"
	return payload


def generate_evaluation(resume: Resume) -> HREvaluation:
	"""Generate and validate a structured HR evaluation for a Resume."""
	logger.info("[WORKFLOW] Building candidate context")
	generated_at = datetime.now(timezone.utc).isoformat()
	context = build_evaluation_context(resume, generated_at)

	if not GEMINI_API_KEY:
		raise MissingWorkflowAPIKeyError("GEMINI_API_KEY is not configured.")

	logger.info("[WORKFLOW] Generating HR evaluation")
	client = OpenAI(api_key=GEMINI_API_KEY, base_url=AI_BASE_URL)
	try:
		response = client.chat.completions.create(
			model=AI_MODEL,
			messages=[
				{"role": "system", "content": WORKFLOW_SYSTEM_PROMPT},
				{
					"role": "user",
					"content": f"Validated resume context:\n{context}",
				},
			],
		)
	except Exception as error:
		logger.exception(
			"[WORKFLOW] Gemini evaluation request failed: exception_type=%s status_code=%s",
			type(error).__name__,
			getattr(error, "status_code", "unavailable"),
		)
		raise EvaluationGenerationError(
			"The HR evaluation could not be generated."
		) from error

	content = (response.choices[0].message.content or "").strip()
	logger.info("[WORKFLOW] Validating evaluation")
	try:
		payload = _normalize_evaluation_payload(
			_extract_json(content), resume, generated_at
		)
		evaluation = HREvaluation.model_validate(payload)
	except (ValidationError, EvaluationGenerationError) as error:
		logger.exception("[WORKFLOW] Evaluation validation failed")
		raise EvaluationGenerationError(
			"Gemini returned an evaluation that failed schema validation."
		) from error

	logger.info("[WORKFLOW] Evaluation validated")
	return evaluation


def load_mock_resume() -> Resume:
	logger.info("[WORKFLOW] Loading resume")
	return load_resume(RESUME_PATH)