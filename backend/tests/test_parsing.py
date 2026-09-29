import json

import pytest

from services.parser import (
	InvalidResumeEncodingError,
	InvalidResumeJsonError,
	ResumeSchemaValidationError,
	parse_resume_file,
)


def test_parse_mock_resume_extracts_all_candidate_sections(resume):
	assert resume.candidate.name == "Arjun Mehta"
	assert resume.education[0].institution == "PES University"
	assert resume.employment_history[0].company == "CloudNova Technologies"
	assert resume.projects[0].name == "Cloud Operations Dashboard"
	assert "AWS" in resume.skills


def test_parse_resume_accepts_empty_optional_collections(resume):
	payload = resume.model_dump()
	payload["certifications"] = []
	payload["projects"] = []

	parsed = parse_resume_file(json.dumps(payload).encode())

	assert parsed.certifications == []
	assert parsed.projects == []


@pytest.mark.parametrize(
	("content", "error_type"),
	[
		(b"not-json", InvalidResumeJsonError),
		(b"\xff\xfe", InvalidResumeEncodingError),
		(json.dumps({"candidate": {}}).encode(), ResumeSchemaValidationError),
	],
)
def test_parse_resume_rejects_malformed_input(content, error_type):
	with pytest.raises(error_type):
		parse_resume_file(content)


def test_parse_resume_rejects_invalid_field_type(resume):
	payload = resume.model_dump()
	payload["candidate"]["email"] = 12345

	with pytest.raises(ResumeSchemaValidationError):
		parse_resume_file(json.dumps(payload).encode())