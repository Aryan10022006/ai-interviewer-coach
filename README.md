# 🎯 AI Interview Prep Coach

**Brutally honest AI interview simulator** with multimodal capabilities (text, audio, video), company-specific research, and complete session history.

## 📖 Quick Start

```bash
# 1. Install core dependencies
pip install -r requirements.txt

# 2. Install multimodal features (optional)
pip install -r requirements_multimodal.txt

# 3. Configure API keys in .env
GOOGLE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional: for Whisper STT & premium TTS

# 4. Choose your interface:

# Text-only interview (basic)
streamlit run app.py

# Enhanced with video analysis
streamlit run app_enhanced.py

# 🆕 MULTIMODAL: Audio + Video (speak & show yourself)
streamlit run app_multimodal.py

# View past interview sessions
streamlit run session_viewer.py
```

📘 **[READ COMPLETE_DOCUMENTATION.md FOR FULL DETAILS](COMPLETE_DOCUMENTATION.md)**  
🎥 **[READ MULTIMODAL_INTEGRATION_GUIDE.md FOR AUDIO/VIDEO](MULTIMODAL_INTEGRATION_GUIDE.md)**

---

## 🌟 Key Features

### Multi-Agent Architecture

Eight specialized AI agents working together:

1. **👤 ProfilerAgent**: Extracts skills, gaps, weaknesses from resume vs JD
2. **🔍 ResearcherAgent**: Fetches company culture & expectations (Tavily)
3. **📄 ResumeAnalyzerAgent**: Pre-interview grading with company fit analysis
4. **🎯 StrategyAgent**: Plans interview strategy & question types
5. **🎤 InterviewerAgent**: Ruthless interviewer with pushback system
6. **📹 VisionCoachAgent**: Analyzes body language & confidence (video)
7. **🤔 CriticAgent**: Brutally honest scoring using STAR framework
8. **📊 ReportAgent**: Comprehensive performance breakdown

### Unique Capabilities

✅ **Pushback System**: If score ≤2/10, question is rephrased more aggressively  
✅ **Early Termination**: Poor performance = interview ends early (realistic)  
✅ **Video Analysis**: Real-time body language & confidence scoring  
✅ **🆕 Multimodal Mode**: Speak answers (STT) + AI speaks questions (TTS)  
✅ **🆕 Live Transcription**: See what you're saying in real-time  
✅ **Company-Aware**: Resume analyzer uses Researcher to evaluate company fit  
✅ **Live Coaching**: STAR framework tips appear in sidebar after each answer  
✅ **Session History**: All interviews saved to SQLite with full transcripts  
✅ **100% FREE**: Google Gemini + Groq Llama 3.3 + Tavily (no credit card)

## 🏆 Why This Wins (Evaluation Scorecard)

| Criteria | How We Win |
|----------|------------|
| **1. Problem Understanding** | Context-aware simulation adapts to YOUR profile and THE specific company |
| **2. Technical Depth** | LangGraph state machine with conditional edges, RAG for company intel |
| **3. Creativity** | **"Live Agent Thoughts"** sidebar shows real-time AI reasoning - users see how they're being judged |
| **4. System Architecture** | Clear separation: `state.py` (shared state) → `agents.py` (specialists) → `graph.py` (orchestration) → `app.py` (UI) |
| **5. Coding Ability** | Modular design, type hints, docstrings explaining prompt engineering choices |
| **6. Communication** | Transparent "Agent Reasoning Trace" visible in UI |

## 🛠️ System Architecture

```
INPUT (Resume + Job + Company)
    ↓
[PROFILER AGENT] → Extracts skills, gaps, weaknesses
    ↓
[RESEARCHER AGENT] → Fetches company culture (Tavily Search)
    ↓
[STRATEGY AGENT] → Plans interview arc & persona
    ↓
    ┌─────────────────────────────────┐
    │   INTERVIEW LOOP (LangGraph)    │
    │                                 │
    │  [INTERVIEWER] Ask Question     │
    │         ↓                       │
    │  [USER] Provide Answer          │
    │         ↓                       │
    │  [CRITIC] Score Silently (STAR) │
    │         ↓                       │
    │  [STAGE CHECK] Continue or End? │
    │         ↓                       │
    └─────────────────────────────────┘
    ↓
[REPORT AGENT] → Comprehensive feedback
```

### 🔄 State Management (The Brain)

All agents share a **central state object** (`AgentState` in `state.py`):

- **Input Phase**: `resume_text`, `job_description`, `company_name`
- **Analysis Phase**: `profile_analysis`, `company_intel`, `question_strategy`
- **Interview Phase**: `conversation_history`, `current_question`, `current_answer`
- **Evaluation Phase**: `feedback_log`, `current_answer_score`, `coaching_tip`
- **Meta**: `interview_stage`, `interviewer_persona`, `agent_reasoning`

This is passed through the LangGraph state machine, allowing agents to coordinate without tight coupling.

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file:

```bash
OPENAI_API_KEY=sk-your-openai-key
TAVILY_API_KEY=tvly-your-tavily-key  # Optional but recommended
```

> **Note**: The system will work without Tavily (uses fallback company data), but real-time research makes it much better.

### 3. Run the App

```powershell
streamlit run app.py
```

### 4. Use the Interface

#### Complete Workflow

**1. Setup Phase** (Collecting Your Information)
- Enter your **full name** (e.g., "John Smith")
- Enter **target company** (e.g., "Microsoft", "Google")
- Upload **resume PDF** OR paste text
- Paste **job description** for the role
- Click "Start Interview" or "Analyze Resume First"

**2. Resume Analysis Phase** (Optional)
- AI analyzes your resume against JD
- Company-specific fit analysis
- ATS compatibility score (0-100)
- Fatal flaws & improvement tips
- Grade: A/B/C/D/F
- Decision: Fix resume or proceed

**3. Interview Phase** (Choose Your Mode)

**Text Mode:**
- Type answers in text box
- Submit after each question
- See real-time feedback in sidebar

**Video Mode:**
- Webcam captures body language
- Type answers + get confidence score
- Non-verbal coaching tips

**Multimodal Mode:**
- 🎤 Speak your answer (STT transcribes)
- 📹 Webcam analyzes confidence
- 🔊 AI speaks questions (TTS)
- See live transcription
- Submit when done speaking

**4. Real-Time Feedback**
- Score after each answer (1-10)
- Strengths & weaknesses
- Improvement tips (STAR framework)
- Pushback if score ≤2 (question rephrased)
- Early termination if consistently poor

**5. Report Phase**
- Overall score & verdict
- Question-by-question breakdown
- Skills analysis (matched/missing)
- Improvement roadmap
- Saved to database with session ID

**6. Review History**
- Run `streamlit run session_viewer.py`
- View all past interviews
- Filter by name, company, score
- Export data for analysis

## 📁 Project Structure

```
AI_Interview_prep_coach/
│
├── 📄 Core System (Brain - Unchanged)
│   ├── state.py              # Shared state definition (AgentState)
│   ├── agents.py             # All 8 agent implementations
│   ├── graph.py              # LangGraph orchestrator (state machine)
│   ├── db_manager.py         # SQLite persistence layer
│   ├── resume_analyzer.py    # Pre-interview resume grading
│   └── pdf_processor.py      # PDF text extraction
│
├── 🎨 User Interfaces
│   ├── app.py                # Text-only interview (basic)
│   ├── app_enhanced.py       # Video analysis (OpenCV)
│   ├── app_multimodal.py     # 🆕 Audio/Video (WebRTC + STT + TTS)
│   └── session_viewer.py     # Session history browser
│
├── 🧩 Multimodal Components (NEW)
│   ├── multimodal_components.py  # STT/TTS/Video sampling engines
│   ├── requirements_multimodal.txt  # Audio/video dependencies
│   └── MULTIMODAL_INTEGRATION_GUIDE.md  # Implementation guide
│
├── 📚 Documentation
│   ├── README.md             # This file (overview)
│   ├── COMPLETE_DOCUMENTATION.md  # Full system reference
│   ├── V2_UPGRADE_SUMMARY.md      # "Strict mode" changes
│   ├── LOGGING_GUIDE.md           # Debugging reference
│   └── FINAL_SUMMARY.md           # Recent updates
│
├── ⚙️ Configuration
│   ├── requirements.txt      # Core dependencies
│   ├── .env                  # API keys (you create this)
│   └── .gitignore
│
└── 💾 Data
    └── interview_sessions.db # SQLite database (auto-created)
```

## 🎨 The "Wow Factor" - Live Agent Thoughts

The sidebar shows **real-time agent reasoning**:

```
🧠 Live Agent Thoughts
━━━━━━━━━━━━━━━━━━━━━
🤔 Critic: Scored 7/10 - confident tone detected

Questions Asked: 4
Current Stage: TECHNICAL
Interviewer Persona: Challenging

📊 Profile Analysis
Matched Skills: Python, AWS, SQL
Missing Skills: Kubernetes, GraphQL
Weaknesses to Probe:
- Vague project descriptions
- Limited scalability experience

Last Answer Score: 7/10
💡 Tip: Add more specific metrics to strengthen impact
```

This transparency demonstrates **explainability** - users understand WHY the AI is asking certain questions.

## 🧠 Technical Highlights

### 1. Dynamic Persona Injection

The interviewer adapts tone based on performance:

```python
persona_tones = {
    "supportive": "Be encouraging and give hints",
    "neutral": "Be professional and balanced",
    "challenging": "Be direct and probe deeper"
}
```

### 2. STAR Method Evaluation

The Critic Agent uses structured analysis:

```python
# Checks:
1. Did they answer the specific question?
2. Was answer structured (STAR framework)?
3. Confidence vs hesitation detection
4. Red flags (vague, defensive, off-topic)
```

### 3. Conditional Interview Flow

LangGraph routing logic:

```python
def should_continue_interview(state):
    if question_count >= 8:
        return "report"
    if stage == "complete":
        return "report"
    return "interview"  # Loop back
```

### 4. Real-World Research (RAG)

Tavily searches for:
- `"[Company] engineering culture interview process"`
- Recent company news
- Interview question patterns

Results feed into question generation for hyper-relevance.

## 🔧 Customization

### Change Interview Length

In `graph.py`, modify:

```python
if question_count >= 8:  # Change to 5, 10, etc.
    return "report"
```

### Adjust Difficulty

In `agents.py`, edit persona prompts:

```python
persona_tones = {
    "brutal": "Ask extremely difficult questions with no hints"
}
```

### Add More Stages

In `graph.py`, expand stage logic:

```python
elif count <= 9:
    state['interview_stage'] = 'system_design'
```

## 🎓 Learning Outcomes

This project demonstrates:

- ✅ **Multi-agent coordination** (not just prompt chaining)
- ✅ **State machines** with conditional edges
- ✅ **RAG** (Retrieval Augmented Generation)
- ✅ **Prompt engineering** for specific behaviors
- ✅ **UI/UX** for complex AI systems
- ✅ **Entity extraction** and semantic matching

## 🐛 Troubleshooting

**Issue**: "No module named langgraph"
```powershell
pip install langgraph
```

**Issue**: API key errors
- Check `.env` file exists and has valid keys
- System works without Tavily (uses fallback data)

**Issue**: Interview loops forever
- Check `graph.py` conditional logic
- Verify `question_count` increments properly

## 🎥 Multimodal Interview Experience (NEW!)

### Three Interface Modes

| Mode | File | Input | Output | Best For |
|------|------|-------|--------|----------|
| **Text** | `app.py` | ⌨️ Keyboard | 📝 Text | Fast practice, no camera |
| **Video** | `app_enhanced.py` | ⌨️ Keyboard + 📹 Webcam | 📝 Text + Body language feedback | Non-verbal coaching |
| **🆕 Multimodal** | `app_multimodal.py` | 🎤 Voice + 📹 Webcam | 🔊 AI speaks + 📝 Transcription | Realistic interview simulation |

### How Multimodal Mode Works

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER                          │
│  (Converts audio/video to text for the brain)              │
│                                                              │
│  🎤 Microphone → STT (Whisper/Google) → Text                │
│  📹 Webcam → Frame Sampling (3s) → Confidence Score         │
│  📝 Text → TTS (OpenAI/gTTS) → 🔊 Audio                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓ (Text only - brain doesn't know source)
┌────────────────────────────────────────────────────────────┐
│                    BRAIN LAYER (UNCHANGED)                  │
│  ProfilerAgent → ResearcherAgent → InterviewerAgent →      │
│  CriticAgent → ReportAgent                                 │
│                                                             │
│  LangGraph State Machine (agents.py, graph.py, state.py)  │
└────────────────────────────────────────────────────────────┘
```

### Key Principle: Brain is Untouched

The multimodal layer is a **pure interface adapter**:
- STT converts your speech → text
- Brain processes text (doesn't know if typed or spoken)
- TTS converts AI response → speech
- Vision analysis → confidence score → added to state

**No changes to agents.py, graph.py, or state.py!** 🎯

### Features

✅ **Speech-to-Text**: Speak your answers (OpenAI Whisper or Google Speech)  
✅ **Text-to-Speech**: AI speaks questions (OpenAI TTS or gTTS)  
✅ **Live Transcription**: See what you're saying in real-time  
✅ **Video Analysis**: Body language scoring every 3 seconds  
✅ **Mode Toggle**: Switch between text/audio/video anytime  
✅ **Graceful Fallbacks**: Falls back to text if WebRTC fails  

### Setup

```bash
# Install multimodal dependencies
pip install streamlit-webrtc av pydub gTTS SpeechRecognition

# Optional: Premium features
pip install elevenlabs  # Ultra-realistic TTS

# Configure .env (optional)
OPENAI_API_KEY=sk-...  # For Whisper STT + Premium TTS
ELEVENLABS_API_KEY=... # For ultra-realistic voice

# Run multimodal interface
streamlit run app_multimodal.py
```

**Free alternatives (no API key needed):**
- STT: Google Speech Recognition (built-in)
- TTS: gTTS (Google Text-to-Speech)

### Performance

| Component | Latency | Quality |
|-----------|---------|---------|
| STT (Whisper) | ~1s | 95%+ accuracy |
| STT (Google) | Real-time | 85-90% accuracy |
| TTS (OpenAI) | ~1s | Natural voice |
| TTS (gTTS) | ~1s | Robotic voice |
| Video Sampling | 3s intervals | Smooth UX |

---

## 📝 Enhanced User Input Collection

The system collects comprehensive user information:

### Required Information

1. **Candidate Name**: Collected at interview start
2. **Resume**: PDF upload or text paste (extracted automatically)
3. **Job Description**: Target role requirements
4. **Company Name**: For company-specific research

### Data Flow

```python
# Input Phase (app.py, app_multimodal.py)
candidate_name = st.text_input("Your Name:", "John Doe")
company = st.text_input("Target Company:", "Microsoft")
job_desc = st.text_area("Job Description:", height=150)

# Resume handling
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
if uploaded_file:
    resume_text = extract_text_from_pdf(uploaded_file)
else:
    resume_text = st.text_area("Or paste resume text:", height=200)

# Validation
if all([candidate_name, resume_text, job_desc, company]):
    session_id = create_session(
        candidate_name=candidate_name,
        company=company,
        role=extract_role_from_jd(job_desc),
        resume_length=len(resume_text)
    )
    # Start interview...
```

### Database Storage

All user information persisted to `interview_sessions.db`:

```sql
-- sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    candidate_name TEXT,      -- From input form
    company TEXT,             -- From input form
    role TEXT,                -- Extracted from JD
    start_time TEXT,
    end_time TEXT,
    overall_score REAL,
    resume_length INTEGER,    -- Character count
    -- ... more fields
);
```

### Session Viewer

View all past sessions with full details:

```bash
streamlit run session_viewer.py
```

Features:
- Filter by candidate name, company, score
- Full Q&A transcripts
- Profile analysis (skills matched/missing)
- Performance statistics

---

## 📝 Future Enhancements

- [x] Voice input/output (speech recognition) - ✅ **DONE: app_multimodal.py**
- [x] Video analysis (body language via webcam) - ✅ **DONE: app_enhanced.py**
- [ ] Multi-round interviews (technical → behavioral → system design)
- [ ] Peer comparison (how you rank vs others for same role)
- [ ] Export to PDF with charts
- [ ] Emotion detection from facial expressions
- [ ] Filler word counter ("um", "uh", "like")
- [ ] Speaking pace analysis (too fast/slow)

## 🙏 Credits

Built with:
- **LangChain/LangGraph**: Agent orchestration
- **OpenAI GPT-4**: Natural language understanding
- **Tavily**: Real-time web search
- **Streamlit**: Interactive UI

---

## 🎯 Demo Script (For Presentation)

1. **Show Architecture Diagram**: Explain the agent coordination
2. **Live Demo**: 
   - Input a real resume + job
   - Point out "Live Agent Thoughts" sidebar
   - Show how interviewer adapts after weak answer
3. **Show Report**: Highlight STAR method scoring
4. **Code Walkthrough**: 
   - Open `agents.py` - explain prompt engineering
   - Open `graph.py` - show conditional edges
5. **Innovation Pitch**: "Unlike chatbots, this COORDINATES agents. The Critic influences the Interviewer WITHOUT the user seeing it - that's the sophistication."

**Key Message**: "This isn't a scripted Q&A. It's a dynamic simulation that REACTS to you, just like a real interviewer would."
