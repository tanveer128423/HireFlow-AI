import json
import logging
import re
from pathlib import Path

from models.schemas import HREvaluation

logger = logging.getLogger(__name__)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
MOCK_HR_RECIPIENT = "hr-admissions@company.mock"


def evaluation_filename(evaluation: HREvaluation) -> str:
	name = re.sub(r"[^A-Za-z0-9]+", "_", evaluation.candidate_name).strip("_")
	return f"{name}_HR_Evaluation.json"


def generate_evaluation_file(evaluation: HREvaluation) -> Path:
	logger.info("[DISPATCH] Generating evaluation file")
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	output_path = OUTPUT_DIR / evaluation_filename(evaluation)
	output_path.write_text(
		json.dumps(evaluation.model_dump(mode="json"), indent=2),
		encoding="utf-8",
	)
	return output_path


def build_hr_submission_payload(evaluation: HREvaluation) -> dict[str, object]:
	return evaluation.model_dump(mode="json")


def build_hr_email_body(evaluation: HREvaluation) -> str:
	return "\n".join(
		[
			f"Hello HR Admissions,",
			"",
			f"Please review the completed hiring evaluation for {evaluation.candidate_name}.",
			"",
			f"Candidate: {evaluation.candidate_name}",
			f"Email: {evaluation.email}",
			f"Recommended role: {evaluation.recommended_role}",
			f"Years of experience: {evaluation.years_of_experience if evaluation.years_of_experience is not None else 'Not specified in resume'}",
			f"Primary skills: {', '.join(evaluation.primary_skillset) or 'Not specified in resume'}",
			f"Employment gaps: {', '.join(evaluation.employment_gaps) or 'None documented'}",
			"",
			f"Recommendation: {evaluation.recommendation_reason}",
			"",
			"The complete structured evaluation is attached.",
		]
	)


def dispatch_evaluation_email(evaluation: HREvaluation) -> dict[str, object]:
	logger.info("[DISPATCH] Simulating email delivery")
	filename = evaluation_filename(evaluation)
	return {
		"status": "prepared",
		"candidate_name": evaluation.candidate_name,
		"recipient": MOCK_HR_RECIPIENT,
		"email_subject": f"Candidate Evaluation - {evaluation.candidate_name}",
		"email_body": build_hr_email_body(evaluation),
		"attachment_generated": True,
		"attachment_filename": filename,
	}
