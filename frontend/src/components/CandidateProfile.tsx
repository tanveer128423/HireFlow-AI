import type { UploadResponse } from "../types";

function CandidateProfile({ data }: { data: UploadResponse }) {
  const stats = [
    ["Education", data.resume.education_count],
    ["Employment", data.resume.employment_count],
    ["Projects", data.resume.project_count],
    ["Skills", data.resume.skill_count],
  ];

  return (
    <section className="panel candidate-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">02 / Candidate overview</p>
          <h2>{data.candidate.name}</h2>
        </div>
        <span className="ready-badge">Resume ready</span>
      </div>
      <div className="candidate-meta">
        <span>{data.candidate.email}</span>
        <span>{data.candidate.location}</span>
      </div>
      <div className="stat-grid">
        {stats.map(([label, value]) => (
          <div className="stat" key={label}>
            <strong>{value}</strong>
            <span>{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

export default CandidateProfile;
