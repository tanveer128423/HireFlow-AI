import json

from services import dispatcher


def test_generate_evaluation_file_writes_expected_artifact(
	monkeypatch, tmp_path, evaluation
):
	monkeypatch.setattr(dispatcher, "OUTPUT_DIR", tmp_path)

	path = dispatcher.generate_evaluation_file(evaluation)

	assert path.name == "Arjun_Mehta_HR_Evaluation.json"
	assert json.loads(path.read_text(encoding="utf-8"))["candidate_name"] == "Arjun Mehta"


def test_dispatch_email_contains_candidate_and_attachment_details(evaluation):
	result = dispatcher.dispatch_evaluation_email(evaluation)

	assert result["status"] == "prepared"
	assert result["candidate_name"] == "Arjun Mehta"
	assert result["attachment_generated"] is True
	assert "Arjun Mehta" in result["email_body"]


def test_submission_payload_matches_evaluation(evaluation):
	assert dispatcher.build_hr_submission_payload(evaluation) == evaluation.model_dump(mode="json")