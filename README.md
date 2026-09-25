# HireFlow AI

> A grounded AI workspace for turning a candidate resume into a reviewable HR evaluation and automated dispatch workflow.

HireFlow AI is an AI-powered recruitment workflow that allows a recruiter to upload a candidate resume, ask natural-language questions about the candidate, generate a structured HR evaluation, and dispatch the completed evaluation as a downloadable artifact or simulated HR email.

The system is designed around one principle: **AI should reason over the provided resume, not invent information that is not present in the source document.**

---

## 1. Problem

Recruiters often spend significant time manually reviewing resumes, searching for specific information, identifying employment gaps, and transferring candidate details into internal evaluation forms.

HireFlow AI demonstrates how this process can be converted into a single workflow:

```text
Resume
   ↓
Resume Parsing
   ↓
Structured Candidate Information
   ↓
AI-Powered Q&A
   ↓
HR Evaluation Generation
   ↓
Validation
   ↓
Download / HR Dispatch
```

The goal is not to replace the recruiter. The goal is to make candidate information easier to inspect, verify, and transfer into an HR workflow.

---

# 2. Core Features

## Resume Upload & Parsing

The application accepts a mock resume represented as structured JSON.

The sample candidate contains:

* Personal information
* Education
* Employment history
* Technical skills
* Projects
* Cloud experience
* Employment gaps

The mock resume intentionally contains a grey area:

**Employment gap: September 2023 to August 2025**

The system surfaces this gap instead of assuming a reason for it.

---

## Natural-Language Candidate Q&A

Recruiters can ask questions about the candidate using natural language.

Example:

```text
Does this candidate have cloud deployment experience?
```

The system can answer using information contained in the resume.

Another example:

```text
What are the candidate's technical skills?
```

The response is presented as:

```text
Grounded in resume
```

This allows the recruiter to distinguish source-grounded information from unsupported assumptions.

Example answer:

```text
Arjun Mehta has experience with AWS.

Work Experience:
As a Software Engineer at CloudNova Technologies,
he deployed application services using AWS.

Certifications:
AWS Cloud Practitioner.

Projects:
Used AWS in the Cloud Operations Dashboard project.

Listed Skills:
AWS.
```

---

# 3. Agentic HR Evaluation Workflow

The main workflow goes beyond simply answering questions.

After the resume is analyzed, the recruiter can select:

**Generate Evaluation**

The AI workflow produces a structured HR evaluation containing:

* Candidate name
* Suggested role
* Years of documented experience
* Primary skillset
* Education
* Employment summary
* Employment gaps
* Key projects
* Cloud experience
* Technical strengths
* Potential concerns
* Evidence-based reasoning

The generated evaluation is then validated before being presented to the recruiter.

The final workflow is:

```text
Candidate Resume
       ↓
Resume Data
       ↓
AI Reasoning
       ↓
Evaluation Fields
       ↓
Schema / Output Validation
       ↓
Validated HR Evaluation
       ↓
       ├── Download Evaluation
       │
       └── Send to HR
```

This orchestration is the agentic part of the application because the AI output becomes an actionable artifact that moves through multiple stages of the workflow.

---

# 4. Example Candidate

The included mock candidate is:

**Arjun Mehta**

Location:

**Bengaluru, India**

Education:

**B.Tech in Computer Science and Engineering**

University:

**PES University**

Employment includes:

### CloudNova Technologies

**Software Engineer**

Documented responsibilities include:

* React dashboard development
* REST API development using Node.js and Express
* MongoDB and PostgreSQL
* Docker containerization
* AWS deployments
* Code reviews and sprint planning

### Independent / Freelance Projects

**Technical Product Engineer**

Documented work includes:

* AI-powered web applications
* React and TypeScript
* Python and FastAPI
* LangChain
* Retrieval-Augmented Generation
* Product workflow design

The resume also contains a documented employment gap:

```text
September 2023 → August 2025
```

HireFlow AI reports the gap but does not invent an explanation for it.

---

# 5. System Architecture

```text
┌──────────────────────────────┐
│        React Frontend        │
│                              │
│  Resume Upload               │
│  Candidate Overview          │
│  AI Q&A                      │
│  HR Evaluation               │
│  Download / Dispatch         │
└──────────────┬───────────────┘
               │
               │ REST API
               ↓
┌──────────────────────────────┐
│        FastAPI Backend       │
│                              │
│  Resume Routes               │
│  AI Service                  │
│  Evaluation Workflow         │
│  Dispatch Service            │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│        Gemini Model          │
│                              │
│  Candidate Q&A               │
│  Evaluation Generation      │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│      Structured Output       │
│                              │
│  HR Evaluation JSON          │
│  Downloadable Artifact       │
│  Mock HR Dispatch            │
└──────────────────────────────┘
```

---

# 6. Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS

## Backend

* Python
* FastAPI
* Uvicorn

## AI

* Google Gemini
* OpenAI-compatible client interface
* Custom AI service layer

## Workflow

* Custom Python orchestration
* Structured JSON evaluation
* Output validation
* Mock dispatch service

## Development

* Git
* GitHub
* REST APIs

---

# 7. Backend API Flow

The backend exposes the workflow through REST endpoints.

### Resume Upload

```http
POST /api/resume/upload
```

Responsible for ingesting the candidate resume and preparing it for analysis.

---

### Candidate Q&A

```http
POST /api/resume/query
```

Receives a recruiter question and returns an answer grounded in the provided resume.

Example:

```json
{
  "question": "What are the candidate's technical skills?"
}
```

---

### Evaluation Generation

```http
POST /api/resume/evaluate
```

Generates the structured HR evaluation from the candidate information.

---

### Evaluation Dispatch

```http
POST /api/resume/dispatch
```

Simulates sending the generated evaluation to:

```text
hr-admissions@company.mock
```

The application also provides a downloadable evaluation artifact.

---

# 8. Prompt Strategy

A major design requirement of HireFlow AI is preventing the model from treating missing information as facts.

The prompts therefore follow a grounded approach.

## Principle 1: Resume as the source of truth

The AI is instructed to use only the supplied candidate information.

Conceptually:

```text
You are analyzing a candidate resume.

Use only information contained in the provided resume.

Do not invent:
- employment history
- skills
- certifications
- education
- dates
- responsibilities
- reasons for employment gaps

If the information is not available, explicitly state that it
is not specified in the resume.
```

---

## Principle 2: Evidence-based answers

The Q&A layer is instructed to answer questions using relevant evidence from the resume.

For example, when asked:

```text
Does the candidate have cloud experience?
```

The model should identify evidence such as:

* AWS listed as a skill
* AWS deployment experience
* AWS-related project experience
* AWS Cloud Practitioner certification

Rather than simply answering:

```text
Yes.
```

the system provides the supporting evidence.

---

## Principle 3: No unsupported explanations

The resume contains an employment gap:

```text
September 2023 → August 2025
```

The system should report:

```text
Employment gap documented from September 2023 to August 2025.
The resume does not specify the reason for the gap.
```

It should not generate explanations such as:

```text
The candidate was studying.
```

unless that information exists in the resume.

---

## Principle 4: Structured evaluation output

The evaluation workflow asks the model to produce structured information instead of unrestricted prose.

The output is normalized and validated before being shown in the UI.

This makes the AI output easier for the frontend to consume and reduces the possibility of malformed evaluation data.

---

# 9. Why the Workflow Is Agentic

The AI is not only being used as a chatbot.

The system performs a sequence of actions:

```text
1. Receive candidate data
        ↓
2. Analyze candidate information
        ↓
3. Answer recruiter questions
        ↓
4. Generate evaluation fields
        ↓
5. Validate the generated evaluation
        ↓
6. Create an HR-ready artifact
        ↓
7. Dispatch or download the artifact
```

The important part is that the output of one stage becomes the input to the next stage.

This creates an automated workflow rather than a standalone AI chat interface.

---

# 10. Output Example

A simplified evaluation structure looks like:

```json
{
  "candidate_name": "Arjun Mehta",
  "role": "Full Stack Software Engineer",
  "years_documented": 3.0,
  "primary_skillset": [
    "React",
    "Node.js",
    "TypeScript",
    "Python",
    "FastAPI",
    "PostgreSQL",
    "Docker",
    "AWS"
  ],
  "education": {
    "degree": "B.Tech in Computer Science and Engineering",
    "institution": "PES University"
  },
  "employment_gaps": [
    {
      "start": "2023-09",
      "end": "2025-08"
    }
  ],
  "potential_concerns": [
    "Documented employment gap from September 2023 to August 2025"
  ]
}
```

The actual generated evaluation contains additional evidence and candidate information.

---

# 11. Error Handling

The application handles failures at the API and AI-service level.

For example, if the AI provider is temporarily unavailable, the backend returns an error rather than presenting an invented response.

During development, the application encountered a temporary Gemini provider `503 UNAVAILABLE` response caused by model demand.

The AI service was tested independently and subsequently returned successful responses.

Successful workflow requests currently return:

```text
POST /api/resume/query       → 200 OK
POST /api/resume/evaluate    → 200 OK
POST /api/resume/dispatch    → 200 OK
```

---

# 12. Running the Project Locally

## Backend

Navigate to the backend:

```bash
cd backend
```

Activate the virtual environment:

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key
AI_MODEL=your_model
AI_BASE_URL=your_base_url
```

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8002
```

Backend:

```text
http://127.0.0.1:8002
```

API documentation:

```text
http://127.0.0.1:8002/docs
```

---

## Frontend

Navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```

---

# 13. Demo Flow

The complete demonstration can be performed in the following order:

### Step 1: Upload

Upload:

```text
mock_resume.json
```

The system parses the candidate information.

### Step 2: Candidate Overview

The application displays:

* Education
* Employment
* Projects
* Skills

### Step 3: Ask AI

Ask:

```text
What are the candidate's technical skills?
```

Then ask:

```text
Does this candidate have cloud deployment experience?
```

Then ask:

```text
Are there any employment gaps?
```

The responses should remain grounded in the resume.

### Step 4: Generate Evaluation

Click:

```text
Generate Evaluation
```

The AI creates the structured HR evaluation.

### Step 5: Review

Review:

* Primary skillset
* Education
* Employment
* Employment gaps
* Projects
* Cloud experience
* Technical strengths
* Potential concerns

### Step 6: Dispatch

Use:

```text
Download Evaluation
```

or:

```text
Send to HR
```

The dispatch workflow simulates sending the completed evaluation to:

```text
hr-admissions@company.mock
```

---

# 14. Project Structure

The project is organized around the frontend application and backend workflow.

A representative structure is:

```text
HireFlow-AI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── services/
│   │   ├── ai_service.py
│   │   └── workflow.py
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── mock_data/
│   └── mock_resume.json
│
├── README.md
├── .gitignore
└── ...
```

The exact directory structure may vary depending on the final repository organization.

---

# 15. Security Considerations

API credentials are kept outside the source code using environment variables.

The repository should never contain:

```text
GEMINI_API_KEY=actual-secret-key
```

Instead, use an `.env.example` file:

```env
GEMINI_API_KEY=your_api_key_here
AI_MODEL=your_model_here
AI_BASE_URL=your_base_url_here
```

The actual `.env` file should be included in `.gitignore`.

---

# 16. Current Scope

This implementation intentionally uses mock resume data to demonstrate the complete workflow within the 24-hour assignment window.

The system currently demonstrates:

```text
Mock Resume
    ↓
AI Q&A
    ↓
AI Evaluation
    ↓
Validation
    ↓
Download
    ↓
Mock HR Dispatch
```

The architecture is designed so that real document ingestion and production integrations can be added later.

---

# 17. Future Improvements

If development continued for another week, the following improvements would be implemented.

## Real Resume Parsing

Add support for:

* PDF
* DOCX
* TXT

The application could extract text directly from uploaded resumes rather than relying on mock JSON.

## OCR

Add OCR support for scanned resumes and image-based documents.

## Retrieval-Augmented Generation

For larger documents or collections of candidate documents, introduce a vector database and retrieval layer.

The flow would become:

```text
Resume
   ↓
Document Extraction
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
   ↓
Relevant Context
   ↓
LLM
```

## Persistent Candidate Database

Store candidates and their evaluations in a database.

This would allow recruiters to:

* Search candidates
* Reopen previous evaluations
* Track evaluation history
* Compare candidate information
* Maintain audit records

## Real Email Integration

Replace the mock dispatch service with a real transactional email provider.

## Human Approval Workflow

Before dispatching an evaluation, add an explicit HR review and approval stage:

```text
AI Generated
     ↓
Human Review
     ↓
Approve / Edit
     ↓
Dispatch
```

This would make the workflow more appropriate for a real recruitment environment.

## Authentication

Add recruiter authentication and role-based access control.

## Audit Logs

Record:

* Who uploaded a resume
* Who asked questions
* What evaluation was generated
* Who edited it
* Who approved it
* When it was dispatched

---

# 18. Design Philosophy

HireFlow AI is built around three principles:

### Grounded

Candidate information should come from the resume rather than unsupported AI assumptions.

### Reviewable

The recruiter should be able to inspect the evidence behind the generated evaluation.

### Actionable

The workflow should produce something useful beyond a chat response, such as a structured evaluation that can be downloaded or dispatched.

The result is a workflow where AI assists the recruiter with information extraction, reasoning, and administrative automation while keeping the generated evaluation reviewable.

---

# 19. Demo

Demo video:

**[Add demo video link here]**

Repository:

**[Add GitHub repository link here]**

Live application:

**N/A / Local demonstration**

---

# 20. Assignment Deliverables

| Deliverable                  | Status                     |
| ---------------------------- | -------------------------- |
| Mock resume ingestion        | Completed                  |
| Natural-language Q&A         | Completed                  |
| Resume-grounded responses    | Completed                  |
| HR evaluation generation     | Completed                  |
| Structured evaluation output | Completed                  |
| Downloadable evaluation      | Completed                  |
| Mock HR dispatch             | Completed                  |
| System design documentation  | Included                   |
| Prompt strategy              | Included                   |
| Future improvements          | Included                   |
| Demo video                   | Add link before submission |

---

## Conclusion

HireFlow AI demonstrates an end-to-end AI recruitment workflow that transforms a resume into structured, reviewable candidate information and an actionable HR evaluation.

The system combines resume-grounded AI Q&A with an automated evaluation and dispatch pipeline, demonstrating how an LLM can be integrated into a practical business workflow rather than being used only as a conversational interface.
