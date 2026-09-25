import json
from typing import Any

from pydantic import ValidationError

from models.schemas import Resume


class ResumeParseError(ValueError):
	"""Base error for invalid resume input."""


class InvalidResumeEncodingError(ResumeParseError):
	"""Raised when resume bytes are not valid UTF-8."""


class InvalidResumeJsonError(ResumeParseError):
	"""Raised when resume text is not valid JSON."""


class ResumeSchemaValidationError(ResumeParseError):
	"""Raised when parsed JSON does not match the Resume schema."""


def parse_resume_file(file_bytes: bytes) -> Resume:
	"""Decode, parse, and validate a JSON resume document."""
	try:
		resume_text = file_bytes.decode("utf-8")
	except UnicodeDecodeError as error:
		raise InvalidResumeEncodingError("Resume file must be valid UTF-8.") from error

	try:
		payload: Any = json.loads(resume_text)
	except json.JSONDecodeError as error:
		raise InvalidResumeJsonError("Resume file must contain valid JSON.") from error

	try:
		return Resume.model_validate(payload)
	except ValidationError as error:
		raise ResumeSchemaValidationError(
			"Resume JSON does not match the expected schema."
		) from error
