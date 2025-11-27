# 🎯 AI Interview Prep Coach - Complete System Documentation

**Version:** 3.0 (Multi-Agent System with Video/Audio Analysis)  
**Last Updated:** November 27, 2025  
**FREE APIs:** Google Gemini + Groq Llama 3.3 + Tavily

---

## 📚 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture & Data Flow](#architecture--data-flow)
3. [Agent System](#agent-system)
4. [Video & Audio Enhancement](#video--audio-enhancement)
5. [Database & Session Management](#database--session-management)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [File Structure](#file-structure)
9. [API Configuration](#api-configuration)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 System Overview

### What Is This?

A **brutally honest AI interview simulator** that:
- ✅ Analyzes your resume for company-specific fit
- ✅ Conducts realistic technical + behavioral interviews
- ✅ Provides real-time feedback (verbal + non-verbal)
- ✅ Tracks body language via webcam (optional)
- ✅ Saves all sessions to database for review
- ✅ Uses 100% FREE APIs (no credit card needed)

### Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Strict Evaluation** | No sugar-coating - honest scoring (1-10/10) | ✅ |
| **Pushback System** | Rephrases questions if answer too weak (≤2/10) | ✅ |
| **Early Termination** | Ends interview if consistent poor performance | ✅ |
| **Resume Analysis** | Pre-interview resume evaluation with company fit | ✅ |
| **Video Analysis** | Body language, eye contact, confidence scoring | ✅ |
| **Live Coaching** | Real-time tips after each answer | ✅ |
| **Database History** | All sessions saved, fully searchable | ✅ |
| **Session Viewer** | Review past interviews with full transcript | ✅ |

---

## 🏗️ Architecture & Data Flow

### Phase 1: Preparation (Analyzing You)

```
User Input:
├─ Resume (PDF or text)
├─ Job Description
└─ Company Name

       ↓

ProfilerAgent (Gemini Pro)
├─ Extracts skills, experience, red flags
├─ Matches skills to JD requirements
└─ Returns: matched_skills[], missing_skills[], weaknesses[]

       ↓

ResearcherAgent (Tavily + Gemini)
├─ Searches: "{company} engineering culture expectations"
├─ Synthesizes: What this company values
└─ Returns: company_intel (culture, tech stack, interview style)

       ↓

ResumejAnalyzerAgent (Optional - Pre-interview)
├─ Fetches company expectations from Researcher
├─ Evaluates: ATS score, fatal flaws, section scores
├─ Analyzes: Company fit (match_level, gaps, tailoring tips)
└─ Returns: Grade (A-F) + improvement recommendations

       ↓

StrategyAgent (Gemini Pro)
├─ Reads: Profile + Research + JD
├─ Plans: Interview strategy (stages, question types)
└─ Returns: question_strategy[] (intro, technical, behavioral)
```

### Phase 2: Interview Loop (Testing You)

```
InterviewerAgent (Groq Llama 3.3 - 300+ tokens/sec)
├─ Generates question based on strategy + past answers
├─ Persona: Senior Staff Engineer (demanding, specific)
└─ Asks: "Walk me through your distributed systems work..."

       ↓

User Answers + Webcam Capture (if enabled)
├─ Text answer typed in Streamlit
└─ Frame captured from webcam (base64 encoded)

       ↓

VisionCoachAgent (Gemini Flash - Multimodal)  ← VIDEO ANALYSIS
├─ Analyzes: Body language, eye contact, facial expression
├─ Scores: Confidence (1-10), Engagement (1-10)
├─ Detects: Fidgeting, poor posture, nervous gestures
└─ Returns: non_verbal_feedback + coaching tips

       ↓

CriticAgent (Gemini Pro)
├─ Evaluates answer using STAR framework
├─ Checks: Specificity, depth, metrics, relevance
├─ Scores: 1-10/10 (brutal honesty)
├─ Provides: Strengths, weaknesses, improvement tip
└─ Integrates: Vision analysis (if video enabled)

       ↓

Decision Node: Continue? Pushback? End?

IF score ≤ 2/10 → PUSHBACK
├─ InterviewerAgent rephrases same question
├─ Demands: "Give CONCRETE example with project names, metrics"
└─ Allows 2 pushback attempts max

IF avg score < 3.5 over 3+ questions → EARLY TERMINATION
├─ Save reason: "Performance below bar (avg 2.8/10)"
└─ Skip to final report

IF questions < 8 AND score acceptable → CONTINUE LOOP

ELSE → Generate Final Report
```

### Phase 3: Final Report (What You Learned)

```
ReportAgent (Gemini Pro)
├─ Aggregates: All Q&A, scores, feedback
├─ Analyzes: Patterns (weak on system design, strong on coding)
├─ Generates: Final verdict + improvement roadmap
└─ Includes: Video analysis summary (if enabled)

       ↓

Database Saves:
├─ sessions table: Overall score, verdict, termination reason
├─ qa_logs table: Every Q&A with score, feedback
└─ profile_analysis table: Skills, weaknesses, red flags

       ↓

User Reviews:
├─ View report in app
└─ Open session_viewer.py to see full history
```

---

## 🤖 Agent System

### Agent Roster

| Agent | Model | Temperature | Role | Input | Output |
|-------|-------|-------------|------|-------|--------|
| **ProfilerAgent** | Gemini Pro | 0.3 | Analyze resume & JD | Resume text, JD | Skills, gaps, weaknesses |
| **ResearcherAgent** | Gemini Pro | 0.7 | Research company | Company name | Culture, tech, expectations |
| **ResumeAnalyzerAgent** | Gemini Flash | 0.3 | Pre-interview eval | Resume, JD, company | Grade, ATS score, company fit |
| **StrategyAgent** | Gemini Pro | 0.5 | Plan interview | Profile, research, JD | Question strategy |
| **InterviewerAgent** | Groq Llama 3.3 | 0.7 | Ask questions | Strategy, past Q&A | Next question |
| **VisionCoachAgent** | Gemini Flash | 0.3 | Analyze video | Webcam frame (base64) | Body language feedback |
| **CriticAgent** | Gemini Pro | 0.3 | Score answers | Question, answer, video | Score, strengths, weaknesses |
| **ReportAgent** | Gemini Pro | 0.5 | Final summary | All Q&A, scores | Verdict, improvement plan |

### Agent Personalities

**ProfilerAgent:**
- "I've analyzed 10,000+ resumes. I can spot BS a mile away."
- Strict JSON output, no fallbacks
- Identifies red flags mercilessly

**InterviewerAgent (Ruthless Persona):**
- "I'm a Senior Staff Engineer at {company}. I've conducted 500+ interviews."
- "I don't accept vague answers. Give me SPECIFICS."
- "You claimed 5 years experience but can't explain this basic concept?"
- Demands: Project names, metrics, technical details

**CriticAgent (Brutally Honest):**
- Score 1-2: "Unacceptable. Too vague, no substance."
- Score 3-4: "Weak. Missing depth and examples."
- Score 5-6: "Acceptable but lacks technical detail."
- Score 7-8: "Good! Clear STAR format with metrics."
- Score 9-10: "Excellent! Perfect answer."

---

## 📹 Video & Audio Enhancement

### What Is app_enhanced.py?

The **enhanced version** adds real-time video analysis to standard interviews.

### Video Analysis Features

| Feature | Technology | What It Does |
|---------|-----------|--------------|
| **Webcam Capture** | OpenCV (cv2) | Captures frames at 640x480 resolution |
| **Face Detection** | Gemini Flash (multimodal) | Detects face position, eye contact |
| **Body Language** | Gemini Flash (vision) | Analyzes posture, fidgeting, gestures |
| **Confidence Scoring** | Vision + LLM | Scores 1-10 based on non-verbal cues |
| **Real-time Coaching** | Streamlit sidebar | Shows tips: "Maintain eye contact with camera" |

### How Video Analysis Works

**1. Webcam Setup:**
```python
# app_enhanced.py
cap = cv2.VideoCapture(0)  # Open default camera
ret, frame = cap.read()     # Capture single frame
cap.release()               # Release camera
```

**2. Frame Processing:**
```python
# Convert BGR → RGB
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# Resize for efficiency
img.thumbnail((640, 480))
# Encode to base64
buffer = io.BytesIO()
img.save(buffer, format="JPEG")
frame_b64 = base64.b64encode(buffer.getvalue()).decode()
```

**3. Vision Analysis:**
```python
# VisionCoachAgent receives base64 frame
state['current_video_frame'] = frame_b64

# Gemini Flash analyzes image + context
prompt = f"""
Analyze this interview candidate's video frame.

CONTEXT:
Question: "{question}"
Answer: "{answer}"

EVALUATE:
1. Eye contact (looking at camera? distracted?)
2. Facial expression (confident? nervous? engaged?)
3. Posture (upright? slouching?)
4. Gestures (natural? fidgeting?)

SCORE:
- Confidence: 1-10
- Engagement: 1-10
"""

response = gemini_flash.generate_content([prompt, image])
```

**4. Feedback Integration:**
```python
# CriticAgent combines verbal + non-verbal
verbal_score = evaluate_star_framework(answer)  # 7/10
video_feedback = vision_coach.analyze(frame)     # Confidence: 5/10

# Final feedback includes both
feedback = {
    'verbal_score': 7,
    'non_verbal_score': 5,
    'tip': 'Good answer, but work on eye contact - look at camera more'
}
```

### Audio Enhancement (Future Feature)

**Planned Features:**
- Speech-to-text (Google Speech API / Whisper)
- Tone analysis (confident vs hesitant)
- Filler word detection ("um", "uh", "like")
- Pacing analysis (too fast, too slow)

**Why Not Implemented Yet:**
- Streamlit doesn't have native audio recording widgets
- Would require WebRTC or custom JavaScript
- Focus currently on text + video (most impactful)

### Running Enhanced Version

```bash
# Basic version (no video)
streamlit run app.py

# Enhanced version (with video analysis)
streamlit run app_enhanced.py
```

**System Requirements:**
- Webcam connected
- Browser permissions: Allow camera access
- Python packages: `opencv-python`, `pillow`

**Performance:**
- Frame capture: ~100ms
- Gemini Flash analysis: ~500ms
- Total overhead: <1 second per answer

---

## 💾 Database & Session Management

### Database Schema

**File:** `interview_sessions.db` (SQLite)

**Table: sessions**
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    candidate_name TEXT,
    company TEXT,
    role TEXT,
    start_time TEXT,
    end_time TEXT,
    overall_score REAL,
    final_verdict TEXT,
    resume_length INTEGER,
    total_questions INTEGER,
    early_termination TEXT
);
```

**Table: qa_logs**
```sql
CREATE TABLE qa_logs (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    question_number INTEGER,
    stage TEXT,           -- 'intro', 'technical', 'behavioral'
    question TEXT,
    answer TEXT,
    answer_length INTEGER,
    critic_score REAL,
    critic_strengths TEXT,
    critic_weaknesses TEXT,
    critic_tip TEXT,
    sentiment TEXT,
    timestamp TEXT,
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

**Table: profile_analysis**
```sql
CREATE TABLE profile_analysis (
    session_id INTEGER PRIMARY KEY,
    matched_skills TEXT,    -- JSON array
    missing_skills TEXT,    -- JSON array
    strengths TEXT,         -- JSON array
    weaknesses TEXT,        -- JSON array
    experience_level TEXT,
    red_flags TEXT,         -- JSON array
    FOREIGN KEY(session_id) REFERENCES sessions(id)
);
```

### Session Lifecycle

**1. Session Creation:**
```python
# When user starts interview
session_id = db_manager.create_session(
    candidate_name="John Doe",
    company="Google",
    role="Senior SWE",
    resume_length=len(resume_text)
)
```

**2. Q&A Logging:**
```python
# After each answer
db_manager.save_qa_step(
    session_id=session_id,
    question_number=3,
    stage="technical",
    question="Explain how you'd design a rate limiter",
    answer=user_answer,
    feedback={
        'score': 7,
        'strengths': 'Good algorithm choice',
        'weaknesses': 'Missing distributed systems context',
        'tip': 'Discuss Redis implementation'
    }
)
```

**3. Profile Saving:**
```python
# After profiling phase
db_manager.save_profile(
    session_id=session_id,
    profile={
        'matched_skills': ['Python', 'AWS', 'Docker'],
        'missing_skills': ['Kubernetes', 'Terraform'],
        'weaknesses': ['System design', 'Distributed systems'],
        'red_flags': ['Job hopping (3 jobs in 2 years)']
    }
)
```

**4. Session Completion:**
```python
# At interview end
db_manager.end_session(
    session_id=session_id,
    overall_score=6.8,
    verdict="Candidate shows promise but needs more depth...",
    early_termination=None  # Or "Performance below bar"
)
```

### Session Viewer Usage

**Launch viewer:**
```bash
streamlit run session_viewer.py
```

**Features:**
- 📋 **List View**: All sessions sorted by date
- 🔍 **Filters**: By company, score, termination status
- 📝 **Transcript**: Full Q&A with scores
- 👤 **Profile**: Skills, gaps, weaknesses
- 📊 **Stats**: Score distribution, stage breakdown
- 🔎 **Raw Data**: JSON export

**Use Cases:**
- Track improvement over time
- Identify weak topics (system design? behavioral?)
- Compare performance across companies
- Export data for analysis

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9+
- Google API Key (FREE - no credit card)
- Groq API Key (FREE - beta access)
- Tavily API Key (FREE tier - 1,000 searches/month)

### Step 1: Clone & Install

```bash
# Clone repository
git clone <repo-url>
cd AI_Interview_prep_coach

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```
streamlit
langchain
langgraph
google-generativeai
groq
tavily-python
python-dotenv
opencv-python
pillow
pypdf2
pdfplumber
```

### Step 2: Get API Keys

**Google Gemini (FREE):**
1. Go to: https://aistudio.google.com/app/apikey
2. Click "Get API Key"
3. Copy key (starts with `AIza...`)

**Groq (FREE):**
1. Go to: https://console.groq.com/keys
2. Sign up with GitHub/Google
3. Create API key

**Tavily (FREE):**
1. Go to: https://tavily.com/
2. Sign up
3. Get API key (1,000 free searches/month)

### Step 3: Configure Environment

Create `.env` file:
```bash
# Google Gemini
GOOGLE_API_KEY=AIzaSyC...your_key_here

# Groq (for fast interviewer)
GROQ_API_KEY=gsk_...your_key_here

# Tavily (for company research)
TAVILY_API_KEY=tvly-...your_key_here
```

### Step 4: Test Setup

```bash
python test_setup.py
```

**Expected output:**
```
✅ Google Gemini API: Connected
✅ Groq API: Connected
✅ Tavily API: Connected
✅ Database: interview_sessions.db created
```

### Step 5: Run Application

**Basic version (no video):**
```bash
streamlit run app.py
```

**Enhanced version (with video):**
```bash
streamlit run app_enhanced.py
```

**Session viewer:**
```bash
streamlit run session_viewer.py
```

---

## 📖 Usage Guide

### Workflow: Complete Interview

**1. Start Application**
```bash
streamlit run app.py
```

**2. Input Phase**
- Enter your name
- Paste job description
- Enter company name
- Upload resume (PDF) OR paste text

**3. Resume Analysis (Optional)**
- Click "Analyze Resume First"
- View: Grade (A-F), ATS score, company fit
- See: Fatal flaws, red flags, tailoring tips
- Decision: Fix resume or proceed

**4. Interview Phase**
- Click "Start Interview Directly" or continue after analysis
- System runs preparation (Profile → Research → Strategy)
- First question appears

**5. Answer Questions**
- Type answer in text box
- Click "Submit Answer"
- View real-time feedback in sidebar:
  - Score (1-10)
  - Strengths
  - Weaknesses
  - Improvement tip

**6. Pushback System**
- If score ≤2/10: Question rephrased
- More demanding version: "Give me SPECIFICS"
- Max 2 pushback attempts

**7. Early Termination**
- If avg score <3.5 over 3+ questions
- System says: "Interview ended early - performance below bar"
- Saves reason to database

**8. Final Report**
- After 8 questions or early termination
- View: Overall score, verdict, improvement roadmap
- All data saved to database

**9. Review History**
```bash
streamlit run session_viewer.py
```
- See all past sessions
- View full transcripts
- Compare performance

### Resume Analysis Workflow

**What You Get:**

**Overall Grade:** A/B/C/D/F
**ATS Score:** 0-100 (keyword matching)

**Company Fit Analysis:**
- Match Level: Excellent/Good/Fair/Poor
- What company expects: "Google values distributed systems..."
- What resume shows: "Strong backend, no open-source"
- Critical gaps: ["No distributed systems experience"]
- Tailoring tips: ["Add Redis/Kafka projects to highlight scalability"]

**Fatal Flaws:**
- Resume is 3+ pages (too long)
- Missing contact information
- Generic objective statement

**Section Scores:**
- Summary: 7/10
- Experience: 8/10
- Skills: 6/10
- Education: 9/10
- Projects: 5/10

**Improvement Tips:**
1. Add measurable outcomes (increased X by Y%)
2. Include open-source contributions
3. Highlight distributed systems work

### Live Coaching System

**During Interview:**

**Score ≤2/10:**
```
🚨 CRITICAL: Answer too weak!

Problem: Too vague, no depth
Fix it: Use STAR format with measurable outcomes

Framework:
- Situation: Set context (project, timeline, team size)
- Task: Your responsibility (what YOU owned)
- Action: What YOU did (not "we") - be specific
- Result: Measurable impact (numbers!)

Example:
"I led migration of monolith to microservices (S).
My task was ensuring zero downtime (T).
I implemented feature flags + canary deployments (A).
Result: 99.99% uptime, 40% faster deploys (R)."
```

**Score 3-6/10:**
```
⚠️ Weak answer - needs more depth
💡 Add specific examples with technical details
```

**Score 7-10/10:**
```
✅ Good! / 🌟 Excellent!
```

---

## 📁 File Structure

```
AI_Interview_prep_coach/
├── agents.py                    # All agent implementations
├── graph.py                     # LangGraph workflow orchestration
├── state.py                     # AgentState definition
├── db_manager.py                # SQLite persistence
├── resume_analyzer.py           # Pre-interview resume evaluation
├── pdf_processor.py             # PDF text extraction
├── app.py                       # Main Streamlit UI (basic)
├── app_enhanced.py              # Streamlit UI with video analysis
├── session_viewer.py            # Session history viewer (NEW)
├── test_setup.py                # API connection testing
├── requirements.txt             # Python dependencies
├── .env                         # API keys (YOU CREATE THIS)
├── interview_sessions.db        # SQLite database (auto-created)
└── COMPLETE_DOCUMENTATION.md    # This file
```

### Key Files Explained

**agents.py** (650+ lines)
- All 8 agent classes
- Strict JSON parsing (no fallbacks)
- Ruthless interviewer persona
- Vision analysis for video frames

**graph.py** (340+ lines)
- LangGraph state machine
- Nodes: prepare, interview, pushback, critique, report
- Conditional routing: continue? pushback? end?
- Database integration

**app.py** (300+ lines)
- Streamlit UI with 3 phases
- Resume upload (PDF/text)
- Live coaching sidebar
- Session management

**app_enhanced.py** (340+ lines)
- Everything in app.py PLUS:
- Webcam capture (OpenCV)
- Real-time video analysis
- Non-verbal feedback

**session_viewer.py** (420+ lines - NEW)
- Full session history
- Filters by company/score
- Q&A transcript viewer
- Performance stats

**db_manager.py** (200+ lines)
- SQLite wrapper functions
- Auto-initialization
- Session CRUD operations

**resume_analyzer.py** (350+ lines)
- Pre-interview resume grading
- ATS scoring
- Company fit analysis (uses Researcher)
- Improvement recommendations

---

## 🔧 API Configuration

### Google Gemini

**Models Used:**
- `gemini-2.0-flash-exp` - Fast, multimodal (vision + text)
- `gemini-1.5-pro` - Deep reasoning

**Rate Limits:**
- Flash: 15 RPM, 1,500/day
- Pro: 2 RPM, 50/day

**Cost:** FREE (no credit card)

**Configuration:**
```python
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

gemini_flash = genai.GenerativeModel(
    'gemini-2.0-flash-exp',
    generation_config={'temperature': 0.3}
)

gemini_pro = genai.GenerativeModel(
    'gemini-1.5-pro',
    generation_config={'temperature': 0.5}
)
```

### Groq

**Model Used:**
- `llama-3.3-70b-versatile` - 300+ tokens/sec

**Rate Limits:**
- 30 RPM, 14,400/day

**Cost:** FREE (beta)

**Configuration:**
```python
from groq import Groq

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7
)
```

### Tavily

**Usage:** Company research

**Rate Limits:**
- 1,000 searches/month (FREE)
- 5 requests/minute

**Configuration:**
```python
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

results = tavily_client.search(
    query="Google engineering culture expectations",
    max_results=5
)
```

---

## 🐛 Troubleshooting

### "API Key Invalid"

**Problem:** `google.generativeai.types.generation_types.BlockedPromptException`

**Solution:**
1. Check `.env` file exists
2. Verify API key format: `AIzaSyC...`
3. Test: `python test_setup.py`

### "Rate Limit Exceeded"

**Problem:** Too many requests to Gemini Pro (2 RPM limit)

**Solution:**
- Use Gemini Flash for non-critical agents
- Add delays between calls
- Monitor usage in Google AI Studio

### "Camera Not Working"

**Problem:** OpenCV can't access webcam

**Solution:**
1. Check browser permissions (allow camera)
2. Close other apps using camera (Zoom, Teams)
3. Use `app.py` instead (no video needed)
4. Test: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`

### "Database Locked"

**Problem:** SQLite file locked (multiple processes)

**Solution:**
- Close all Streamlit instances
- Delete `interview_sessions.db`
- Restart app (auto-recreates)

### "JSON Parsing Error"

**Problem:** LLM returned markdown code blocks

**Solution:**
- Already handled in agents.py
- If persists: Check agent logs
- Verify prompt includes: "Return ONLY JSON, no markdown"

### "Pushback Not Triggering"

**Problem:** Score ≤2 but question doesn't rephrase

**Solution:**
- Check graph.py: `should_continue_interview()` logic
- Verify state has `current_question`
- Look for: "🔄 PUSHBACK triggered" in logs

### "Session Not Saving"

**Problem:** Interview completes but no database entry

**Solution:**
- Check db_manager.py imports correctly
- Verify session_id stored in state
- Check terminal for database errors
- Inspect: `interview_sessions.db` with SQLite browser

---

## 🎯 System Features Summary

### What Makes This System Unique

**1. Brutal Honesty (No Sugar-Coating)**
- Scores 1-10 with no grade inflation
- "Unacceptable" vs "Good" vs "Excellent"
- Real interview feedback

**2. Pushback System (Realism)**
- Real interviewers drill deeper on weak answers
- System does same - rephrases question
- Max 2 attempts then moves on

**3. Early Termination (Fail Fast)**
- Consistent poor performance = early end
- Saves time, teaches lessons
- Real interviews do this

**4. Company-Aware Analysis**
- Researcher fetches company culture
- Resume analyzer evaluates fit
- Tailoring tips specific to company

**5. Video Analysis (Non-Verbal)**
- Body language scoring
- Eye contact tracking
- Confidence assessment
- Real-time coaching

**6. Complete History**
- Every session saved
- Full transcript + scores
- Track improvement over time
- Export data

**7. 100% FREE**
- No credit card required
- Generous rate limits
- Production-quality responses

---

## 📞 Support & Contributing

**Issues:** Open GitHub issue with:
- Error message
- Terminal logs
- Steps to reproduce

**Feature Requests:** Describe use case + expected behavior

**Contributing:** PRs welcome for:
- New agent types
- UI improvements
- Database features
- Documentation

---

**Built with ❤️ using LangGraph, Gemini, and Streamlit**
