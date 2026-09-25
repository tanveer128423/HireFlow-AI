import type {
  DispatchMethod,
  DispatchResponse,
  EvaluationResponse,
  Evaluation,
  QueryResponse,
  UploadResponse,
} from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8002";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(response: Response): Promise<ApiError> {
  try {
    const body = (await response.json()) as { detail?: string };
    return new ApiError(
      body.detail || `Request failed with status ${response.status}.`,
      response.status,
    );
  } catch {
    return new ApiError(
      `Request failed with status ${response.status}.`,
      response.status,
    );
  }
}

async function request<T>(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw await parseError(response);
  }
  return (await response.json()) as T;
}

export function uploadResume(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>(`${API_URL}/api/resume/upload`, {
    method: "POST",
    body: formData,
  });
}

export function askResumeQuestion(question: string): Promise<QueryResponse> {
  return request<QueryResponse>(`${API_URL}/api/resume/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export function generateEvaluation(
  resumeId: string,
): Promise<EvaluationResponse> {
  return request<EvaluationResponse>(`${API_URL}/api/resume/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId }),
  });
}

export async function dispatchEvaluation(
  resumeId: string,
  method: DispatchMethod,
  evaluation?: Evaluation,
): Promise<DispatchResponse | Blob> {
  const response = await fetch(`${API_URL}/api/resume/dispatch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume_id: resumeId,
      method,
      ...(evaluation ? { evaluation } : {}),
    }),
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return method === "download"
    ? response.blob()
    : ((await response.json()) as DispatchResponse);
}
