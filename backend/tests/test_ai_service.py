from types import SimpleNamespace

import pytest

from services import ai_service


class ProviderError(Exception):
	def __init__(self, status_code):
		super().__init__(f"provider status {status_code}")
		self.status_code = status_code


def patch_client(monkeypatch, response=None, error=None):
	class FakeClient:
		class chat:
			class completions:
				@staticmethod
				def create(**kwargs):
					if error:
						raise error
					return response

	monkeypatch.setattr(ai_service, "GEMINI_API_KEY", "test-key")
	monkeypatch.setattr(ai_service, "OpenAI", lambda **kwargs: FakeClient())


def test_answer_resume_question_returns_mocked_grounded_answer(
	monkeypatch, fake_openai_response
):
	patch_client(
		monkeypatch,
		fake_openai_response("Based on the provided resume, the candidate has AWS deployment experience."),
	)

	answer, grounded = ai_service.answer_resume_question("Does the candidate have AWS experience?")

	assert "AWS deployment" in answer
	assert grounded is True


def test_answer_resume_question_marks_absent_information_as_not_grounded(
	monkeypatch, fake_openai_response
):
	patch_client(
		monkeypatch,
		fake_openai_response(
			"The resume does not provide enough information to answer this confidently."
		),
	)

	answer, grounded = ai_service.answer_resume_question("What is the candidate's salary?")

	assert grounded is False
	assert "not provide enough information" in answer


@pytest.mark.parametrize("status_code", [503, 429])
def test_answer_resume_question_maps_provider_failures(monkeypatch, status_code):
	patch_client(monkeypatch, error=ProviderError(status_code))

	with pytest.raises(ai_service.ResumeQuestionError):
		ai_service.answer_resume_question("Does the candidate know Python?")


def test_answer_resume_question_rejects_empty_ai_response(monkeypatch, fake_openai_response):
	patch_client(monkeypatch, fake_openai_response(""))

	with pytest.raises(ai_service.ResumeQuestionError, match="empty answer"):
		ai_service.answer_resume_question("What is the candidate's role?")