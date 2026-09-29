import json
from types import SimpleNamespace

import pytest

from services import workflow


def test_calculate_employment_gaps_reports_documented_gap(resume):
	assert workflow.calculate_employment_gaps(resume) == ["2023-09 to 2025-08"]


def test_calculate_employment_gaps_has_no_gap_for_consecutive_periods(resume):
	resume.employment_history[1].start = "2023-09"

	assert workflow.calculate_employment_gaps(resume) == []


def test_calculate_employment_gaps_handles_overlapping_periods(resume):
	resume.employment_history[1].start = "2023-01"

	assert workflow.calculate_employment_gaps(resume) == []


def test_generate_evaluation_validates_and_normalizes_ai_json(
	monkeypatch, resume, evaluation_json, fake_openai_response
):
	class FakeClient:
		class chat:
			class completions:
				@staticmethod
				def create(**kwargs):
					return fake_openai_response(evaluation_json)

	monkeypatch.setattr(workflow, "GEMINI_API_KEY", "test-key")
	monkeypatch.setattr(workflow, "OpenAI", lambda **kwargs: FakeClient())

	evaluation = workflow.generate_evaluation(resume)

	assert evaluation.candidate_name == "Arjun Mehta"
	assert evaluation.employment_gaps == ["2023-09 to 2025-08"]
	assert evaluation.status == "completed"


def test_generate_evaluation_rejects_invalid_json(
	monkeypatch, resume, fake_openai_response
):
	class FakeClient:
		class chat:
			class completions:
				@staticmethod
				def create(**kwargs):
					return fake_openai_response("{invalid")

	monkeypatch.setattr(workflow, "GEMINI_API_KEY", "test-key")
	monkeypatch.setattr(workflow, "OpenAI", lambda **kwargs: FakeClient())

	with pytest.raises(workflow.EvaluationGenerationError, match="failed schema validation"):
		workflow.generate_evaluation(resume)


def test_generate_evaluation_rejects_missing_required_output_field(
	monkeypatch, resume, evaluation_payload, fake_openai_response
):
	evaluation_payload.pop("recommended_role")

	class FakeClient:
		class chat:
			class completions:
				@staticmethod
				def create(**kwargs):
					return fake_openai_response(json.dumps(evaluation_payload))

	monkeypatch.setattr(workflow, "GEMINI_API_KEY", "test-key")
	monkeypatch.setattr(workflow, "OpenAI", lambda **kwargs: FakeClient())

	with pytest.raises(workflow.EvaluationGenerationError, match="schema validation"):
		workflow.generate_evaluation(resume)


def test_generate_evaluation_maps_provider_failure(
	monkeypatch, resume
):
	class FakeClient:
		class chat:
			class completions:
				@staticmethod
				def create(**kwargs):
					raise RuntimeError("provider unavailable")

	monkeypatch.setattr(workflow, "GEMINI_API_KEY", "test-key")
	monkeypatch.setattr(workflow, "OpenAI", lambda **kwargs: FakeClient())

	with pytest.raises(workflow.EvaluationGenerationError):
		workflow.generate_evaluation(resume)