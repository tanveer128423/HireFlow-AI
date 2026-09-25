export type UploadResponse = {
  success: true;
  candidate: {
    name: string;
    email: string;
    location: string;
  };
  resume: {
    education_count: number;
    employment_count: number;
    project_count: number;
    skill_count: number;
  };
};

export type QueryResponse = {
  success: true;
  question: string;
  answer: string;
  grounded: boolean;
};

export type Evaluation = {
  candidate_name: string;
  email: string;
  primary_skillset: string[];
  years_of_experience: number | null;
  education: string;
  employment_summary: string;
  employment_gaps: string[];
  key_projects: string[];
  cloud_experience: string;
  technical_strengths: string[];
  potential_concerns: string[];
  recommended_role: string;
  recommendation_reason: string;
  generated_at: string;
  status: string;
};

export type EvaluationResponse = {
  success: true;
  evaluation: Evaluation;
};

export type DispatchResponse = {
  success: true;
  dispatch: {
    status: "prepared" | "sent" | "simulated" | string;
    candidate_name?: string;
    recipient?: string;
    email_subject?: string;
    email_body?: string;
    attachment_generated?: boolean;
    attachment_filename?: string;
    subject?: string;
    attachment?: string;
  };
  submission?: Evaluation;
};

export type DispatchMethod = "email" | "download";
