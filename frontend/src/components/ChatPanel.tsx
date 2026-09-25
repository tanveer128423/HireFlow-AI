import type { QueryResponse } from "../types";

type ChatPanelProps = {
  question: string;
  answer: QueryResponse | null;
  error: string | null;
  isLoading: boolean;
  onQuestionChange: (question: string) => void;
  onAsk: () => void;
};

const examples = [
  "Cloud experience",
  "Technical skills",
  "Education",
  "Employment history",
  "Projects",
];

function ChatPanel({
  question,
  answer,
  error,
  isLoading,
  onQuestionChange,
  onAsk,
}: ChatPanelProps) {
  return (
    <section className="panel chat-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">03 / Intelligence</p>
          <h2>Ask about the candidate</h2>
        </div>
        <span className="ai-mark">AI</span>
      </div>
      <div className="question-row">
        <input
          value={question}
          onChange={(event) => onQuestionChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) onAsk();
          }}
          placeholder="Ask a question about this resume..."
          aria-label="Resume question"
        />
        <button
          className="dark-button"
          type="button"
          disabled={!question.trim() || isLoading}
          onClick={onAsk}
        >
          {isLoading ? "Thinking..." : "Ask AI"}
        </button>
      </div>
      <div className="chip-row">
        {examples.map((example) => (
          <button
            type="button"
            className="chip"
            key={example}
            onClick={() => onQuestionChange(example)}
          >
            {example}
          </button>
        ))}
      </div>
      {answer && (
        <div className="answer-box">
          <div className="answer-label">
            <span>Answer</span>
            {answer.grounded && (
              <span className="grounded-badge">● Grounded in resume</span>
            )}
          </div>
          <p>{answer.answer}</p>
          <small>Question: {answer.question}</small>
        </div>
      )}
      {error && (
        <div className="workflow-status error chat-error" role="alert">
          {error}
        </div>
      )}
    </section>
  );
}

export default ChatPanel;
