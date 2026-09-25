import type { ReactNode } from "react";
import type { Evaluation } from "../types";

type EducationEntry = {
  degree?: string;
  institution?: string;
  start?: number | string;
  end?: number | string;
};

type EmploymentEntry = {
  company?: string;
  job_title?: string;
  duration?: string;
  responsibilities?: string[];
  technologies?: string[];
};

function parseStructured<T>(value: unknown, fallback: T): T {
  if (typeof value !== "string") return (value as T) ?? fallback;
  try {
    return JSON.parse(value) as T;
  } catch {
    return fallback;
  }
}

function displayValue(value: unknown, fallback = "Not specified in resume") {
  return value === undefined || value === null || value === ""
    ? fallback
    : String(value);
}

function formatMonth(value: unknown) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}$/.test(value)) {
    return displayValue(value);
  }
  const [year, month] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("en", {
    month: "short",
    year: "numeric",
  }).format(new Date(year, month - 1, 1));
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="evaluation-field">
      <span>{label}</span>
      <div>{children}</div>
    </div>
  );
}

function EvaluationForm({ evaluation }: { evaluation: Evaluation }) {
  const education = parseStructured<EducationEntry[]>(evaluation.education, []);
  const employment = parseStructured<EmploymentEntry[]>(
    evaluation.employment_summary,
    [],
  );
  const gaps = parseStructured<string[]>(evaluation.employment_gaps, []);
  const cloudExperience = parseStructured<
    string | string[] | Record<string, unknown>
  >(evaluation.cloud_experience, evaluation.cloud_experience);

  return (
    <div className="evaluation-content">
      <div className="evaluation-hero">
        <div>
          <span className="ready-badge">{evaluation.status}</span>
          <h3>{evaluation.candidate_name}</h3>
          <p>{evaluation.recommended_role}</p>
        </div>
        <div className="experience-score">
          <strong>
            {evaluation.years_of_experience === null ||
            evaluation.years_of_experience === undefined
              ? "—"
              : evaluation.years_of_experience.toFixed(1)}
          </strong>
          <span>years documented</span>
        </div>
      </div>
      <div className="evaluation-grid">
        <Field label="Primary skillset">
          <div className="tag-list">
            {evaluation.primary_skillset.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </Field>
        <Field label="Education">
          <EducationList entries={education} />
        </Field>
        <Field label="Employment summary">
          <EmploymentList entries={employment} />
        </Field>
        <Field label="Employment gaps">
          <GapList items={gaps} />
        </Field>
        <Field label="Key projects">
          <List
            items={evaluation.key_projects}
            empty="Not specified in resume"
          />
        </Field>
        <Field label="Cloud experience">
          <CloudExperience value={cloudExperience} />
        </Field>
        <Field label="Technical strengths">
          <List
            items={evaluation.technical_strengths}
            empty="Not specified in resume"
          />
        </Field>
        <Field label="Potential concerns">
          <List items={evaluation.potential_concerns} empty="None documented" />
        </Field>
      </div>
      <div className="recommendation">
        <span>Recommendation reason</span>
        <p>{evaluation.recommendation_reason}</p>
      </div>
    </div>
  );
}

function EducationList({ entries }: { entries: EducationEntry[] }) {
  if (!entries.length) return <p>Not specified in resume</p>;
  return (
    <div className="education-list">
      {entries.map((entry, index) => (
        <article
          className="education-entry"
          key={`${entry.degree ?? "education"}-${index}`}
        >
          <strong>{displayValue(entry.degree)}</strong>
          <span>{displayValue(entry.institution)}</span>
          <small>
            {entry.start !== undefined || entry.end !== undefined
              ? `${displayValue(entry.start, "Start not specified")} → ${displayValue(entry.end, "End not specified")}`
              : "Dates not specified in resume"}
          </small>
        </article>
      ))}
    </div>
  );
}

function EmploymentList({ entries }: { entries: EmploymentEntry[] }) {
  if (!entries.length) return <p>Not specified in resume</p>;
  return (
    <div className="employment-list">
      {entries.map((entry, index) => (
        <article
          className="employment-entry"
          key={`${entry.company ?? "employment"}-${index}`}
        >
          <div className="employment-entry-header">
            <div>
              <strong>{displayValue(entry.company)}</strong>
              <span>{displayValue(entry.job_title)}</span>
            </div>
            <small>{displayValue(entry.duration)}</small>
          </div>
          {entry.responsibilities?.length ? (
            <div className="employment-detail">
              <b>Responsibilities</b>
              <List
                items={entry.responsibilities}
                empty="Not specified in resume"
              />
            </div>
          ) : null}
          {entry.technologies?.length ? (
            <div className="employment-detail">
              <b>Technologies</b>
              <div className="technology-list">
                {entry.technologies.map((technology) => (
                  <span key={technology}>{technology}</span>
                ))}
              </div>
            </div>
          ) : null}
        </article>
      ))}
    </div>
  );
}

function GapList({ items }: { items: string[] }) {
  if (!items.length) return <p>No documented gaps</p>;
  return (
    <div className="gap-list">
      {items.map((gap) => {
        const [start, end] = gap.split(" to ");
        return (
          <div className="gap-entry" key={gap}>
            <strong>Employment gap</strong>
            <span>
              {formatMonth(start)} → {formatMonth(end)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function StructuredText({ value }: { value: unknown }) {
  if (typeof value === "string") return <p>{value}</p>;
  if (Array.isArray(value))
    return <List items={value.map(String)} empty="Not specified in resume" />;
  if (value && typeof value === "object") {
    return (
      <List
        items={Object.entries(value).map(
          ([key, item]) =>
            `${key}: ${Array.isArray(item) ? item.join(", ") : String(item)}`,
        )}
        empty="Not specified in resume"
      />
    );
  }
  return <p>Not specified in resume</p>;
}

function CloudExperience({ value }: { value: unknown }) {
  if (typeof value === "string") return <p>{value}</p>;
  if (Array.isArray(value)) {
    return <List items={value.map(String)} empty="Not specified in resume" />;
  }
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    const platforms = Array.isArray(record.platforms)
      ? record.platforms.map(String)
      : record.platforms
        ? [String(record.platforms)]
        : [];
    const details = Object.entries(record)
      .filter(([key]) => key !== "platforms")
      .flatMap(([key, item]) => {
        const values = Array.isArray(item) ? item.map(String) : [String(item)];
        return values.map((text) =>
          key === "certifications" &&
          !text.toLowerCase().includes("certification")
            ? `${text} certification.`
            : text,
        );
      });
    return (
      <div className="cloud-experience">
        {platforms.length > 0 && <strong>{platforms.join(" · ")}</strong>}
        {details.length > 0 ? (
          <List items={details} empty="Not specified in resume" />
        ) : (
          <p>Not specified in resume</p>
        )}
      </div>
    );
  }
  return <p>Not specified in resume</p>;
}

function List({ items, empty }: { items: string[]; empty: string }) {
  return items.length ? (
    <ul>
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  ) : (
    <p>{empty}</p>
  );
}

export default EvaluationForm;
