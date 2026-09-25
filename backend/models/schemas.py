import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class Candidate(BaseModel):
	name: str
	email: str
	phone: str
	location: str


class Education(BaseModel):
	degree: str
	institution: str
	start: int
	end: int


class Employment(BaseModel):
	company: str
	job_title: str
	start: str
	end: str
	responsibilities: list[str]
	technologies: list[str]


class Project(BaseModel):
	name: str
	description: str
	technologies: list[str]


class Certification(BaseModel):
	name: str


class Resume(BaseModel):
	candidate: Candidate
	education: list[Education]
	employment_history: list[Employment]
	skills: list[str]
	certifications: list[Certification]
	projects: list[Project]


class HREvaluation(BaseModel):
	candidate_name: str
	email: str
	primary_skillset: list[str]
	years_of_experience: float | None
	education: str
	employment_summary: str
	employment_gaps: list[str]
	key_projects: list[str]
	cloud_experience: str
	technical_strengths: list[str]
	potential_concerns: list[str]
	recommended_role: str
	recommendation_reason: str
	generated_at: str
	status: str


def load_resume(path: str | Path) -> Resume:
	"""Load and validate a resume JSON document."""
	with Path(path).open(encoding="utf-8") as resume_file:
		payload: Any = json.load(resume_file)
	return Resume.model_validate(payload)
