from fastapi.testclient import TestClient

from main import app
from routes import query as query_route
from routes import resume as resume_route
from services import ai_service
from services import workflow


client = TestClient(app)


def test_upload_resume_returns_candidate_and_counts():
	with open("data/mock_resume.json", "rb") as resume_file:
		response = client.post(
			"/api/resume/upload",
			files={"file": ("resume.json", resume_file, "application/json")},
		)

	assert response.status_code == 200
	body = response.json()
	assert body["candidate"]["name"] == "Arjun Mehta"
	assert body["resume"] == {
		"education_count": 1,
		"employment_count": 2,
		"project_count": 2,
		"skill_count": 16,
	}


def test_upload_resume_rejects_empty_and_malformed_files():
	empty = client.post(
		"/api/resume/upload", files={"file": ("resume.json", b"", "application/json")}
	)
	malformed = client.post(
		"/api/resume/upload", files={"file": ("resume.json", b"{}", "application/json")}
	)

	assert empty.status_code == 400
	assert "empty" in empty.json()["detail"]
	assert malformed.status_code == 400


def test_upload_resume_rejects_non_json_file():
	response = client.post(
		"/api/resume/upload", files={"file": ("resume.txt", b"resume", "text/plain")}
	)

	assert response.status_code == 400


def test_query_resume_returns_mocked_answer(monkeypatch):
	monkeypatch.setattr(
		query_route,
		"answer_resume_question",
		lambda question: ("The candidate has AWS experience.", True),
	)

	response = client.post("/api/resume/query", json={"question": "  Does the candidate know AWS?  "})

	assert response.status_code == 200
	assert response.json() == {
		"success": True,
		"question": "Does the candidate know AWS?",
		"answer": "The candidate has AWS experience.",
		"grounded": True,
	}


def test_query_resume_rejects_empty_question():
	response = client.post("/api/resume/query", json={"question": "   "})

	assert response.status_code == 400


def test_query_resume_maps_provider_failure(monkeypatch):
	monkeypatch.setattr(
		query_route,
		"answer_resume_question",
		lambda question: (_ for _ in ()).throw(ai_service.ResumeQuestionError("provider failed")),
	)

	response = client.post("/api/resume/query", json={"question": "Does the candidate know AWS?"})

	assert response.status_code == 502
	assert response.json()["detail"] == "provider failed"


def test_evaluate_resume_returns_mocked_valid_evaluation(monkeypatch, evaluation):
	monkeypatch.setattr(resume_route, "generate_evaluation", lambda resume: evaluation)

	response = client.post("/api/resume/evaluate", json={"resume_id": "mock_resume"})

	assert response.status_code == 200
	assert response.json()["evaluation"]["candidate_name"] == "Arjun Mehta"


def test_evaluate_resume_rejects_unknown_resume():
	response = client.post("/api/resume/evaluate", json={"resume_id": "missing"})

	assert response.status_code == 404


def test_evaluate_resume_maps_generation_failure(monkeypatch):
	monkeypatch.setattr(
		resume_route,
		"generate_evaluation",
		lambda resume: (_ for _ in ()).throw(
			workflow.EvaluationGenerationError("evaluation provider failed")
		),
	)

	response = client.post("/api/resume/evaluate", json={"resume_id": "mock_resume"})

	assert response.status_code == 502
	assert response.json()["detail"] == "evaluation provider failed"


def test_dispatch_email_returns_submission_and_creates_artifact(
	monkeypatch, tmp_path, evaluation
):
	monkeypatch.setattr(resume_route, "generate_evaluation_file", lambda value: tmp_path / "evaluation.json")
	monkeypatch.setattr(resume_route, "dispatch_evaluation_email", lambda value: {"status": "prepared"})

	response = client.post(
		"/api/resume/dispatch",
		json={"resume_id": "mock_resume", "method": "email", "evaluation": evaluation.model_dump(mode="json")},
	)

	assert response.status_code == 200
	assert response.json()["dispatch"]["status"] == "prepared"
	assert response.json()["submission"]["candidate_name"] == "Arjun Mehta"


def test_dispatch_rejects_incomplete_email_evaluation(evaluation):
	payload = evaluation.model_dump(mode="json")
	payload["status"] = "draft"

	response = client.post(
		"/api/resume/dispatch",
		json={"resume_id": "mock_resume", "method": "email", "evaluation": payload},
	)

	assert response.status_code == 400


def test_dispatch_download_returns_json_artifact(monkeypatch, tmp_path, evaluation):
	path = tmp_path / "Arjun_Mehta_HR_Evaluation.json"
	path.write_text('{"candidate_name":"Arjun Mehta"}', encoding="utf-8")
	monkeypatch.setattr(resume_route, "generate_evaluation_file", lambda value: path)
	monkeypatch.setattr(resume_route, "_generate_mock_evaluation", lambda request: evaluation)

	response = client.post(
		"/api/resume/dispatch",
		json={"resume_id": "mock_resume", "method": "download"},
	)

	assert response.status_code == 200
	assert response.headers["content-type"].startswith("application/json")
	assert response.json()["candidate_name"] == "Arjun Mehta"