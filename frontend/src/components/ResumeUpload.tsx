type ResumeUploadProps = {
  file: File | null;
  isUploading: boolean;
  onFileChange: (file: File | null) => void;
  onAnalyze: () => void;
};

function ResumeUpload({
  file,
  isUploading,
  onFileChange,
  onAnalyze,
}: ResumeUploadProps) {
  return (
    <section className="panel upload-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">01 / Intake</p>
          <h2>Upload a resume</h2>
        </div>
        <span className="status-dot">JSON</span>
      </div>
      <label className="drop-zone">
        <input
          type="file"
          accept=".json,application/json"
          onChange={(event) => onFileChange(event.target.files?.[0] || null)}
        />
        <span className="upload-icon">↑</span>
        <strong>{file ? file.name : "Choose a resume file"}</strong>
        <span>
          {file ? "Ready to analyze" : "Structured JSON resumes supported"}
        </span>
      </label>
      <button
        className="primary-button"
        type="button"
        disabled={!file || isUploading}
        onClick={onAnalyze}
      >
        {isUploading ? "Uploading resume..." : "Analyze Resume"}
        {!isUploading && <span>→</span>}
      </button>
    </section>
  );
}

export default ResumeUpload;
