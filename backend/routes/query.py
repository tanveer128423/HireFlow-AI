from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.ai_service import (
	MissingAPIKeyError,
	ResumeQuestionError,
	answer_resume_question,
)

router = APIRouter()


class ResumeQueryRequest(BaseModel):
	question: str = Field(min_length=1)


@router.post("/query")
def query_resume(request: ResumeQueryRequest) -> dict[str, object]:
	question = request.question.strip()
	if not question:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Question must not be empty.",
		)

	try:
		answer, grounded = answer_resume_question(question)
	except MissingAPIKeyError as error:
		raise HTTPException(
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
			detail=str(error),
		) from error
	except (ResumeQuestionError, ValueError) as error:
		raise HTTPException(
			status_code=status.HTTP_502_BAD_GATEWAY,
			detail=str(error),
		) from error
	except Exception as error:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="The resume could not be loaded or validated.",
		) from error

	return {
		"success": True,
		"question": question,
		"answer": answer,
		"grounded": grounded,
	}