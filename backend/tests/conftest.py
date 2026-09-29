import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from models.schemas import HREvaluation, load_resume


RESUME_PATH = Path(__file__).parents[1] / "data" / "mock_resume.json"


@pytest.fixture
def resume():
	return load_resume(RESUME_PATH)


@pytest.fixture
def evaluation_payload():
	return {
		"candidate_name": "Arjun Mehta",
		"email": "arjun.mehta@example.com",
		"primary_skillset": ["Python", "React", "AWS"],
		"years_of_experience": 3.0,
		"education": "B.Tech in Computer Science and Engineering, PES University",
		"employment_summary": "Software engineering and independent product engineering experience.",
		"employment_gaps": [],
		"key_projects": ["Cloud Operations Dashboard"],
		"cloud_experience": "Documented AWS deployment experience.",
		"technical_strengths": ["API development", "Cloud deployment"],
		"potential_concerns": [],
		"recommended_role": "Full Stack Engineer",
		"recommendation_reason": "The documented experience supports this role.",
		"generated_at": "2026-01-01T00:00:00+00:00",
		"status": "completed",
	}


@pytest.fixture
def evaluation(evaluation_payload):
	return HREvaluation.model_validate(evaluation_payload)


@pytest.fixture
def fake_openai_response():
	def build(content):
		return SimpleNamespace(
			choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
		)

	return build


@pytest.fixture
def evaluation_json(evaluation_payload):
	return json.dumps(evaluation_payload)