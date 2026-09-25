from fastapi import APIRouter, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from models.schemas import HREvaluation
from services.dispatcher import (
	build_hr_submission_payload,
	dispatch_evaluation_email,
	generate_evaluation_file,
)
from services.workflow import (
	EvaluationGenerationError,
	MissingWorkflowAPIKeyError,
	generate_evaluation,
	load_mock_resume,
)

from services.parser import (
	InvalidResumeEncodingError,
	InvalidResumeJsonError,
	ResumeSchemaValidationError,
	parse_resume_file,
)

router = APIRouter()


class ResumeWorkflowRequest(BaseModel):
	resume_id: str = Field(min_length=1)


class ResumeDispatchRequest(ResumeWorkflowRequest):
	method: str = Field(pattern="^(email|download)$")
	evaluation: HREvaluation | None = None


@router.post("/upload")
async def upload_resume(file: UploadFile) -> dict[str, object]:
	filename = file.filename or ""
	if not filename.lower().endswith(".json"):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Only .json resume files are supported.",
		)

	file_bytes = await file.read()
	if not file_bytes:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="The uploaded resume file is empty.",
		)

	try:
		resume = parse_resume_file(file_bytes)
	except (
		InvalidResumeEncodingError,
		InvalidResumeJsonError,
		ResumeSchemaValidationError,
	) as error:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(error),
		) from error

	return {
		"success": True,
		"candidate": {
			"name": resume.candidate.name,
			"email": resume.candidate.email,
			"location": resume.candidate.location,
		},
		"resume": {
			"education_count": len(resume.education),
			"employment_count": len(resume.employment_history),
			"project_count": len(resume.projects),
			"skill_count": len(resume.skills),
		},
	}


def _generate_mock_evaluation(request: ResumeWorkflowRequest) -> HREvaluation:
	if request.resume_id != "mock_resume":
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Resume not found.",
		)
	try:
		return generate_evaluation(load_mock_resume())
	except MissingWorkflowAPIKeyError as error:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=str(error),
		) from error
	except EvaluationGenerationError as error:
		raise HTTPException(
			status_code=status.HTTP_502_BAD_GATEWAY,
			detail=str(error),
		) from error


@router.post("/evaluate")
def evaluate_resume(request: ResumeWorkflowRequest) -> dict[str, object]:
	evaluation = _generate_mock_evaluation(request)
	return {
		"success": True,
		"evaluation": evaluation.model_dump(mode="json"),
	}


@router.post("/dispatch", response_model=None)
def dispatch_resume(request: ResumeDispatchRequest) -> object:
	if request.method == "email" and request.evaluation is not None:
		if request.evaluation.status != "completed":
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Only a completed evaluation can be sent to HR.",
			)
		evaluation = request.evaluation
	else:
		evaluation = _generate_mock_evaluation(request)
	output_path = generate_evaluation_file(evaluation)

	if request.method == "email":
		return {
			"success": True,
			"dispatch": dispatch_evaluation_email(evaluation),
			"submission": build_hr_submission_payload(evaluation),
		}

	return FileResponse(
		path=output_path,
		media_type="application/json",
		filename=output_path.name,
	)