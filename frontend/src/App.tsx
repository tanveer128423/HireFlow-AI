import { useState } from "react";
import CandidateProfile from "./components/CandidateProfile";
import ChatPanel from "./components/ChatPanel";
import EvaluationForm from "./components/EvaluationForm";
import ResumeUpload from "./components/ResumeUpload";
import WorkflowStatus from "./components/WorkflowStatus";
import {
  askResumeQuestion,
  dispatchEvaluation,
  generateEvaluation,
  uploadResume,
  ApiError,
} from "./services/api";
import type { Evaluation, QueryResponse, UploadResponse } from "./types";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [upload, setUpload] = useState<UploadResponse | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [askError, setAskError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isDispatching, setIsDispatching] = useState(false);
  const [dispatchResult, setDispatchResult] = useState<{
    recipient?: string;
    attachmentGenerated?: boolean;
    attachmentFilename?: string;
  } | null>(null);
  const [message, setMessage] = useState<{
    text: string;
    tone: "info" | "success" | "error";
  } | null>(null);

  async function handleAnalyze() {
    if (!file) return;
    setIsUploading(true);
    setMessage(null);
    try {
      const result = await uploadResume(file);
      setUpload(result);
      setAnswer(null);
      setEvaluation(null);
      setMessage({
        text: "Resume uploaded successfully. AI actions are ready when you are.",
        tone: "success",
      });
    } catch (error) {
      setMessage({
        text:
          error instanceof Error
            ? error.message
            : "Unable to upload the resume.",
        tone: "error",
      });
    } finally {
      setIsUploading(false);
    }
  }

  async function handleAsk() {
    if (!question.trim()) return;
    setIsQuerying(true);
    setAskError(null);
    setMessage(null);
    try {
      setAnswer(await askResumeQuestion(question.trim()));
    } catch (error) {
      if (error instanceof ApiError) {
        const isQuotaError =
          error.status === 429 ||
          (error.status === 502 &&
            /quota|rate limit|exhausted/i.test(error.message));
        setAskError(
          isQuotaError
            ? "AI service quota is temporarily exhausted. Please try again later."
            : error.status === 503
              ? "AI model is temporarily unavailable. Please try again in a moment."
              : error.status === 404
                ? "The configured AI model is currently unavailable."
                : error.status >= 500
                  ? "The AI service could not process your request. Please try again."
                  : "Unable to answer that question. Please try again.",
        );
      } else {
        setAskError("Unable to reach the AI service. Please try again.");
      }
    } finally {
      setIsQuerying(false);
    }
  }

  async function handleGenerate() {
    setIsEvaluating(true);
    setMessage(null);
    try {
      const result = await generateEvaluation("mock_resume");
      setEvaluation(result.evaluation);
      setMessage({
        text: "Evaluation generated and validated.",
        tone: "success",
      });
    } catch (error) {
      setMessage({
        text:
          error instanceof Error
            ? error.message
            : "Unable to generate the evaluation.",
        tone: "error",
      });
    } finally {
      setIsEvaluating(false);
    }
  }

  async function handleDispatch(method: "email" | "download") {
    if (!evaluation) return;
    setIsDispatching(true);
    setMessage(null);
    try {
      const result = await dispatchEvaluation(
        "mock_resume",
        method,
        evaluation,
      );
      if (result instanceof Blob) {
        const url = URL.createObjectURL(result);
        const link = document.createElement("a");
        link.href = url;
        link.download = "Arjun_Mehta_HR_Evaluation.json";
        link.click();
        URL.revokeObjectURL(url);
        setMessage({ text: "Evaluation download is ready.", tone: "success" });
      } else {
        setDispatchResult({
          recipient: result.dispatch.recipient,
          attachmentGenerated: result.dispatch.attachment_generated,
          attachmentFilename: result.dispatch.attachment_filename,
        });
        setMessage({
          text:
            result.dispatch.status === "prepared"
              ? "Evaluation prepared for HR."
              : "Evaluation sent to HR successfully.",
          tone: "success",
        });
      }
    } catch (error) {
      setMessage({
        text:
          error instanceof Error
            ? error.message
            : "Unable to dispatch the evaluation.",
        tone: "error",
      });
    } finally {
      setIsDispatching(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="HireFlow AI home">
          <span className="brand-mark">H</span>HireFlow <em>AI</em>
        </a>
        <div className="topbar-note">
          <span className="live-dot" />
          Recruiter workspace <span className="slash">/</span> Local mode
        </div>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">Candidate intelligence workspace</p>
          <h1>
            Make the next
            <br />
            <span>good hire</span> clearer.
          </h1>
          <p className="hero-lede">
            A grounded workspace for turning a resume into confident, reviewable
            hiring decisions.
          </p>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <div className="orbit-ring ring-one" />
          <div className="orbit-ring ring-two" />
          <div className="orbit-core">
            HF<span>AI</span>
          </div>
        </div>
      </section>

      <div className="workspace">
        <div className="workspace-intro">
          <span>Workflow</span>
          <strong>One candidate at a time</strong>
          <span className="intro-line" />
        </div>
        <div className="dashboard-grid">
          <ResumeUpload
            file={file}
            isUploading={isUploading}
            onFileChange={setFile}
            onAnalyze={handleAnalyze}
          />
          <div className="status-column">
            <WorkflowStatus
              message={upload ? "Resume ready" : "No resume uploaded"}
              tone={upload ? "success" : "info"}
            />
            {message && (
              <WorkflowStatus message={message.text} tone={message.tone} />
            )}
          </div>
        </div>

        {upload && <CandidateProfile data={upload} />}

        <div className="section-rule">
          <span>Recruiter tools</span>
        </div>
        <ChatPanel
          question={question}
          answer={answer}
          error={askError}
          isLoading={isQuerying}
          onQuestionChange={setQuestion}
          onAsk={handleAsk}
        />

        <section className="panel evaluation-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">04 / Decision support</p>
              <h2>HR Evaluation</h2>
            </div>
            <button
              className="primary-button compact"
              type="button"
              disabled={isEvaluating}
              onClick={handleGenerate}
            >
              {isEvaluating
                ? "Generating evaluation..."
                : "Generate Evaluation"}
              <span>✦</span>
            </button>
          </div>
          {evaluation ? (
            <EvaluationForm evaluation={evaluation} />
          ) : (
            <div className="empty-state">
              <span className="empty-symbol">✦</span>
              <p>
                Generate a structured evaluation when you are ready to review
                this candidate.
              </p>
            </div>
          )}
        </section>

        {evaluation && (
          <section className="dispatch-strip">
            <div>
              <p className="eyebrow">05 / Next action</p>
              <h2>Dispatch Evaluation</h2>
              <p>
                Send the validated evaluation to the next place it needs to go.
              </p>
            </div>
            <div className="dispatch-actions">
              <button
                className="outline-button"
                type="button"
                disabled={isDispatching}
                onClick={() => handleDispatch("download")}
              >
                ↓ <span>Download Evaluation</span>
              </button>
              <button
                className="dark-button"
                type="button"
                disabled={isDispatching}
                onClick={() => handleDispatch("email")}
              >
                {isDispatching ? "Preparing evaluation..." : "Send to HR →"}
              </button>
            </div>
            {dispatchResult && (
              <div className="dispatch-confirmation">
                <strong>{message?.text}</strong>
                {dispatchResult.recipient && (
                  <span>Recipient: {dispatchResult.recipient}</span>
                )}
                <span>
                  Attachment:{" "}
                  {dispatchResult.attachmentGenerated
                    ? "generated"
                    : "not generated"}
                  {dispatchResult.attachmentFilename
                    ? ` · ${dispatchResult.attachmentFilename}`
                    : ""}
                </span>
              </div>
            )}
          </section>
        )}
      </div>
      <footer>
        <span>HireFlow AI</span>
        <span>Grounded candidate intelligence · 2026</span>
      </footer>
    </main>
  );
}

export default App;
