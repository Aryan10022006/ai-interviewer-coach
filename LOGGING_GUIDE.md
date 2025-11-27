# 🔍 Logging & Debugging Guide

## Overview
The AI Interview Prep Coach now includes comprehensive logging to track agent execution and debug issues.

---

## 📊 What Gets Logged

### 1. **Preparation Phase** (`run_preparation_phase()`)
Shows the sequential execution of initial analysis agents:

```
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
                    PREPARATION PHASE
🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

📊 Step 1: Running Profiler Agent...
   📊 ProfilerAgent: Processing resume (1234 chars)...
   📊 ProfilerAgent: Analyzing JD (567 chars)...
   📊 ProfilerAgent: Calling Gemini Flash for analysis...
   📊 ProfilerAgent: Received 856 chars response
   📊 ProfilerAgent: Successfully parsed JSON
   ✅ Profiler: Found 5 matching skills, identified 3 areas to probe.

🔍 Step 2: Running Researcher Agent...
   🔍 ResearcherAgent: Researching 'Google'...
   🔍 ResearcherAgent: Searching Tavily for 'Google engineering culture interview process'...
   🔍 ResearcherAgent: Found 3 results
   🔍 ResearcherAgent: Synthesizing 2456 chars of data...
   🔍 ResearcherAgent: Calling Gemini Flash to synthesize...
   🔍 ResearcherAgent: Generated 234 char intel summary
   ✅ Researcher: Found 3 sources on Google's interview culture

🎯 Step 3: Running Strategy Agent...
   🎯 StrategyAgent: Planning with 5 matched skills...
   🎯 StrategyAgent: Considering 2 skill gaps...
   🎯 StrategyAgent: Calling Gemini Flash for strategy...
   🎯 StrategyAgent: Generated 345 char strategy
   🎯 StrategyAgent: Set persona to 'neutral'
   ✅ Strategy: Planned neutral interview approach

🎤 Step 4: Generating First Question...
   🎭 InterviewerAgent: Stage=intro, Persona=neutral, Q#1
   🎭 InterviewerAgent: 0 messages in history
   🎭 InterviewerAgent: Generating question with GeminiWrapper...
   🎭 InterviewerAgent: Generated question (123 chars)
   ✅ Interviewer: Asking intro question (#1) in neutral tone

✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
               PREPARATION COMPLETE
✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
```

### 2. **Answer Processing** (`process_user_answer()`)
Shows the evaluation loop for each user response:

```
============================================================
💬 PROCESSING ANSWER #2
============================================================

📹 Running Vision Coach...
   ✅ Body language appears confident with good eye contact

🤔 Running Critic Agent...
   🤔 CriticAgent: Evaluating 456 char answer...
   🤔 CriticAgent: Calling Gemini Flash for evaluation...
   🤔 CriticAgent: Successfully parsed evaluation JSON
   🤔 CriticAgent: Score=8/10, Sentiment=confident
   ✅ Critic: Scored 8/10 - confident tone detected
   Score: 8/10

📈 Stage: TECHNICAL

🎯 Decision: INTERVIEW

🎤 Generating Next Question...
   🎭 InterviewerAgent: Stage=technical, Persona=neutral, Q#3
   🎭 InterviewerAgent: 4 messages in history
   🎭 InterviewerAgent: Generating question with GeminiWrapper...
   🎭 InterviewerAgent: Generated question (234 chars)
   ✅ Interviewer: Asking technical question (#3) in neutral tone
   Question: Can you explain the difference between a list and a tuple in Python...
============================================================
```

### 3. **Final Report Generation** (`ReportAgent`)
Shows comprehensive performance analysis:

```
📊 Generating Final Report...
   📊 ReportAgent: Generating final report...
   📊 ReportAgent: Analyzed 5 answers, avg score=7.4/10
   📊 ReportAgent: 12 messages in transcript
   📊 ReportAgent: Calling Gemini Flash to generate report...
   📊 ReportAgent: Generated 1234 char report
   ✅ Report generated
```

---

## 🎯 Agent Identification

Each agent has a unique emoji identifier:

| Agent | Emoji | Purpose |
|-------|-------|---------|
| **ProfilerAgent** | 📊 | Resume vs JD analysis |
| **ResearcherAgent** | 🔍 | Company intel gathering |
| **StrategyAgent** | 🎯 | Interview strategy planning |
| **InterviewerAgent** | 🎭 | Question generation |
| **CriticAgent** | 🤔 | Answer evaluation |
| **ReportAgent** | 📊 | Final report generation |
| **VisionCoachAgent** | 📹 | Body language analysis |

---

## 🐛 Debugging Common Issues

### Issue 1: GraphRecursionError
**What it means:** The interview loop ran too many times without terminating.

**How to debug:**
1. Check the terminal logs to see which agent keeps repeating
2. Look for the stage progression: `📈 Stage: TECHNICAL`
3. Verify the decision logic: `🎯 Decision: INTERVIEW` or `🎯 Decision: END`

**Solution:** The preparation phase now runs agents directly (not via graph) to avoid loops. Interview phase has proper termination conditions.

### Issue 2: JSON Parse Failures
**Symptoms:** You see warnings like `⚠️ ProfilerAgent: JSON parse failed`

**How to debug:**
1. Check which agent is failing: `📊 ProfilerAgent`, `🤔 CriticAgent`, etc.
2. The log shows the error message: `(Expecting value: line 1 column 1)`
3. All agents have fallback data to continue execution

**Solution:** Agents now include better prompt engineering and fallback mechanisms.

### Issue 3: API Key Issues
**Symptoms:** `❌ Missing` next to API keys at startup

**How to debug:**
1. Check startup logs:
   ```
   🔑 Google API Key: ✅ Found
   🔑 Groq API Key: ✅ Found
   ```
2. Verify `.env` file contains valid keys
3. Check if keys are placeholder values like `your_api_key_here`

**Solution:** Update `.env` with valid API keys.

---

## 📈 Tracking Agent Execution Flow

### Sequential Execution (Preparation Phase)
```
Profile → Research → Strategy → First Question
   ↓         ↓          ↓            ↓
  📊        🔍         🎯           🎭
```

### Loop Execution (Interview Phase)
```
User Answer → Vision (optional) → Critic → Stage Check → Next Question
     ↓              📹                🤔         📈            🎭
     └──────────────────────────────────────────────────────┘
                    (Repeats until "END" decision)
```

### Termination Conditions
The interview ends when:
1. **Question Count ≥ 8:** Reached maximum questions
2. **Stage = "closing":** Completed all interview stages
3. **Average Score < 5:** Candidate struggling too much
4. **Average Score > 9:** Candidate excelling, no need to continue

---

## 🔧 Enabling More Verbose Logging

To add even more detailed logs, edit agents.py:

```python
# Add to any agent's run() method:
print(f"   🔍 DEBUG: State keys = {list(state.keys())}")
print(f"   🔍 DEBUG: Question count = {state.get('question_count', 0)}")
print(f"   🔍 DEBUG: Current stage = {state.get('interview_stage', 'N/A')}")
```

---

## 📝 Log Analysis Tips

### Finding Performance Bottlenecks
1. Look for large character counts: `Received 5000+ chars response`
2. Check Tavily search times: `Found 0 results` (fallback used)
3. Monitor question generation: `Generated question (500+ chars)` (may be too long)

### Verifying Agent Decisions
1. **Stage Progression:** Should go `intro → technical → behavioral → closing`
2. **Score Trends:** Watch for `Score=X/10` to see candidate improvement
3. **Persona Changes:** Check if `Persona=challenging` when candidate struggles

### Understanding Failures
1. **Fallback Usage:** Any `⚠️` indicates fallback was used
2. **JSON Errors:** Shows exact parsing error for debugging
3. **Empty Answers:** `No answer to evaluate, skipping...` means user didn't respond

---

## 🚀 Running Tests with Logging

Use the test script to see logging in action:

```powershell
cd d:\Projects\AI_Interview_prep_coach
python test_logging.py
```

This will simulate an interview and show all agent logs.

---

## 📊 Performance Metrics

The logs track these key metrics:

| Metric | Where to Find | Purpose |
|--------|---------------|---------|
| **Character counts** | `Processing resume (1234 chars)` | Input size validation |
| **API response size** | `Received 856 chars response` | LLM output monitoring |
| **Question count** | `Q#3` | Interview progress |
| **Score progression** | `Score=8/10` | Candidate performance trend |
| **Skill matches** | `Found 5 matching skills` | Profile quality |
| **Research results** | `Found 3 sources` | Data availability |
| **Agent reasoning** | `✅ Profiler: Found...` | High-level summary |

---

## 🎓 Best Practices

1. **Monitor the preparation phase** - It should complete in 4 steps without loops
2. **Check question counts** - Should not exceed 8-10 questions
3. **Verify stage progression** - Should move forward, not get stuck
4. **Watch for fallbacks** - Too many `⚠️` warnings indicate API issues
5. **Track average scores** - Should stabilize after 3-4 questions

---

## 🛠️ Troubleshooting Commands

### View Real-Time Logs
```powershell
# Run Streamlit and watch terminal output
streamlit run app.py

# The logs appear in the terminal where you ran the command
```

### Test Single Agent
```python
from agents import profiler
from state import AgentState

state = {
    'resume_text': 'Sample resume...',
    'job_description': 'Sample JD...'
}

result = profiler.run(state)
# Check terminal for logs
```

### Save Logs to File
```powershell
# Redirect output to file
streamlit run app.py 2>&1 | Tee-Object -FilePath interview_logs.txt
```

---

## 📞 Support

If you encounter issues not covered here:

1. Check the terminal logs for specific error messages
2. Look for `⚠️` or `❌` symbols indicating failures
3. Verify all agents complete their tasks: `✅ Agent: Done`
4. Review the stage progression and decision flow
5. Check API key validity and quota limits

---

## 🎯 Summary

The logging system provides:
- ✅ **Real-time visibility** into agent execution
- ✅ **Error tracking** with fallback mechanisms
- ✅ **Performance metrics** for optimization
- ✅ **Debug information** for troubleshooting
- ✅ **Progress indicators** for user feedback

All logs appear in the terminal where you run `streamlit run app.py`.
