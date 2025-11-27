# 🎯 AI Interview Prep Coach - V2.0 "Strict Mode"

## What Changed: From Friendly Chatbot → Real Interview

### 1. **Ruthless Interviewer Persona**

**Before:** "Great answer! Let's move to the next question..."
**Now:** "I'm going to stop you there. That's too vague for a senior role. Walk me through the TECHNICAL DETAILS..."

The interviewer now behaves like a **Senior Staff Engineer** who:
- ❌ **Doesn't accept vague answers** - Demands specifics with numbers/metrics
- ❌ **Calls out BS** - "You claimed 5 years of React but can't explain hooks?"
- ❌ **Drills deeper on weak answers** - Won't move on until you give substance
- ✅ **Teaches through failure** - Corrects wrong answers and makes you try again

### 2. **Pushback System** (NEW)

**What it does:** If you score ≤2/10, the system DOESN'T move to the next question. Instead:
1. The interviewer **aggressively rephrases** the same question
2. Demands: "Give me a CONCRETE example with project names, your role, metrics"
3. Allows max 2 pushback attempts - if you fail both, marks topic as "FAILED" and moves on

**Example Flow:**
```
Q: "Explain how you'd design a rate limiter"
A: "I'd use Redis"
Score: 2/10 (too brief)

🚨 PUSHBACK: "Simply saying 'Redis' is unacceptable. 
Explain: What algorithm? Token bucket or leaky bucket? 
How do you handle distributed systems? What's the data structure?"

A: [Better answer with details]
Score: 7/10 → Moves to next question
```

### 3. **Early Termination** (Fail Fast)

If you consistently score <3.5/10 over 3+ questions, **interview ends early**:
- System saves: `early_termination_reason = "Performance below bar (avg 2.8/10)"`
- No more questions - straight to final report
- **Real interviews DO this** - they don't waste time on clearly unqualified candidates

### 4. **Database Persistence** (NEW)

Every Q&A is saved to `interview_sessions.db`:

**Tables:**
- `sessions` - Interview metadata (candidate, company, overall score, termination reason)
- `qa_logs` - Every question, answer, score, feedback, sentiment
- `profile_analysis` - Skills matched, gaps, weaknesses, red flags

**Why this matters:**
- You can review past interviews
- Track improvement over time
- See exactly where you failed (which topics, which stages)

### 5. **Live Coaching Sidebar** (NEW)

**Before:** Feedback only at the end
**Now:** Real-time coaching after every answer

**If you score ≤2/10:**
```
🚨 CRITICAL: Answer too weak!
Problem: Too vague, no depth
Fix it: Use STAR format with measurable outcomes

Framework:
- Situation: Set context
- Task: Your responsibility  
- Action: What YOU did (not "we")
- Result: Measurable impact (numbers!)
```

**If you score 3-6/10:**
```
⚠️ Weak answer - needs more depth
💡 Add specific examples with technical details
```

**If you score 7-10/10:**
```
✅ Good! / 🌟 Excellent!
```

### 6. **Stage-Specific Question Types**

**INTRO:** NOT "tell me about yourself" (lazy!)
- "Walk me through your experience with [KEY_SKILL from JD]"

**TECHNICAL:** HARD questions with right/wrong answers
- "Explain time complexity of [ALGORITHM]"
- "Design a system to handle 10M requests/day"
- "Debug this code: [shows actual code with bug]"

**BEHAVIORAL:** Challenging situations (not softball questions)
- "Tell me about a time you FAILED" (not "succeeded")
- "Describe a conflict with a coworker"
- "You missed a critical deadline - walk me through it"

**CLOSING:** Direct about gaps
- "You have limited [MISSING_SKILL] experience. How will you ramp up?"

---

## How to Use V2.0

### For Candidates:
1. **Upload PDF resume** or paste text
2. **Be prepared for pushback** - vague answers will get challenged
3. **Watch the Live Coach** - it tells you HOW to improve in real-time
4. **Use STAR format** for behavioral questions
5. **Give technical details** - not just technology names, but WHY and HOW

### For Evaluators:
1. All data saved to `interview_sessions.db`
2. Query it: `SELECT * FROM sessions WHERE overall_score < 5`
3. Review transcripts: `SELECT * FROM qa_logs WHERE session_id = X`
4. See patterns: Which questions do candidates fail most?

---

## Technical Architecture

### Flow:
```
Profile → Research → Strategy → Interview Loop
                                      ↓
                                 [Critic scores]
                                      ↓
                              Score ≤2? → PUSHBACK (stay on question)
                              Score 3-6? → NEXT (advance)
                              Avg <3.5? → END (terminate early)
```

### Agents:
1. **ProfilerAgent** - Strict JSON parsing, NO fallbacks
2. **ResearcherAgent** - Real company data via Tavily
3. **StrategyAgent** - Plans difficulty based on weaknesses
4. **InterviewerAgent** - Ruthless follow-ups, demands depth
5. **CriticAgent** - Brutally honest scoring (1=terrible, 10=exceptional)
6. **PushbackAgent** (NEW) - Rephrases weak questions aggressively
7. **ReportAgent** - Final verdict with action items

### Database Schema:
```sql
sessions (id, candidate, company, overall_score, early_termination)
qa_logs (session_id, question, answer, critic_score, feedback)
profile_analysis (session_id, matched_skills, missing_skills, weaknesses)
```

---

## Key Improvements Over V1.0

| Feature | V1.0 (Friendly) | V2.0 (Strict) |
|---------|----------------|---------------|
| **Vague Answers** | Accepts them | Pushback system |
| **Weak Performance** | Continues to end | Early termination |
| **Feedback** | Only at end | Live coaching |
| **Persistence** | None | SQLite database |
| **Interviewer Tone** | Supportive | Ruthless but professional |
| **Question Quality** | Generic | Role-specific, challenging |
| **Learning** | Minimal | Teaches through failure |

---

## What Makes This "Real"

✅ **Interviewers DO challenge weak answers** - "That's insufficient. Elaborate."
✅ **Interviewers DO end early** - Won't waste time on clearly unqualified candidates
✅ **Interviewers DO drill on weaknesses** - "You said you're weak at X. Prove you understand it."
✅ **Interviewers DO correct mistakes** - "No, that's wrong. Here's why..."
✅ **Interviewers DO pressure test** - "Your design fails under [SCENARIO]. How do you handle it?"

❌ **Real interviews DON'T:**
- Accept "I don't know" without follow-up
- Move on from terrible answers without comment
- Give participation trophies ("great job!" to everyone)
- Let candidates ramble without redirecting

---

## Installation & Setup

```bash
# Install new dependencies
pip install PyPDF2 pdfplumber

# Run the app
streamlit run app.py

# Database is auto-created on first run
# Location: ./interview_sessions.db
```

---

## Future Enhancements

1. **Voice mode** - Real-time speech-to-text with Groq Whisper
2. **Video analysis** - Body language scoring with Gemini Vision
3. **Custom personas** - FAANG style vs Startup style vs Government contractor
4. **Multi-session tracking** - "You improved 2.3 points since last week!"
5. **Question bank** - Pull from LeetCode, System Design primers
6. **Peer benchmarking** - "87% of candidates answered this better than you"

---

## Summary

**V2.0 transforms the coach from a friendly tutor into a REAL interviewer.**

It's not mean - it's **honest**. It teaches candidates that:
- Vague answers don't fly in real interviews
- Technical depth matters more than buzzwords
- Being challenged is how you learn

The goal: **Prepare candidates for the ACTUAL interview experience**, not a fantasy version of it.
