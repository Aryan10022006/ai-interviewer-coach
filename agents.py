"""
AI Interview Prep Coach - Agent Implementations
Each agent is a specialized node in the LangGraph workflow.
Uses FREE APIs: Gemini (via direct SDK) + Groq (fast interviewer)
"""

import os
from typing import Dict
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json
import re
import base64

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ google-generativeai not installed. Run: pip install google-generativeai")

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ tavily-python not installed. Install for web search: pip install tavily-python")

# Initialize LLMs (FREE APIS)
# Load API keys from Streamlit secrets (Cloud) or .env (Local)
import streamlit as st
from dotenv import load_dotenv

# Try Streamlit secrets first (for Cloud deployment), then .env (for local)
try:
    google_api_key = st.secrets["GOOGLE_API_KEY"]
    groq_api_key = st.secrets["GROQ_API_KEY"]
    print("🔐 Using Streamlit Cloud secrets")
except (FileNotFoundError, KeyError):
    # Fallback to .env for local development
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    print("🔐 Using local .env file")

print(f"🔑 Google API Key: {'✅ Found' if google_api_key and google_api_key != 'your_google_api_key_here' else '❌ Missing'}")
print(f"🔑 Groq API Key: {'✅ Found' if groq_api_key and groq_api_key != 'your_groq_api_key_here' else '❌ Missing'}")

# Configure Gemini (using google-generativeai SDK directly - no auth issues!)
if GEMINI_AVAILABLE and google_api_key and google_api_key != "your_google_api_key_here":
    try:
        genai.configure(api_key=google_api_key)
        # Use the best available models from November 2025
        gemini_flash_model = genai.GenerativeModel('gemini-2.5-flash')  # Fast & smart
        gemini_pro_model = genai.GenerativeModel('gemini-2.5-pro')  # Most intelligent
        print("✅ Gemini 2.5 configured successfully (Flash + Pro)")
    except Exception as e:
        gemini_flash_model = None
        gemini_pro_model = None
        print(f"⚠️ Gemini configuration failed: {e}")
else:
    gemini_flash_model = None
    gemini_pro_model = None
    print("⚠️ Gemini not configured. Set GOOGLE_API_KEY in .env or Streamlit secrets")

# Groq: Super fast (for live interviewer)
groq_llm = None
if groq_api_key and groq_api_key != "your_groq_api_key_here":
    try:
        groq_llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=groq_api_key
        )
    except Exception as e:
        print(f"⚠️ Groq unavailable: {e}")

# Wrapper class to make Gemini work like LangChain LLM
class GeminiWrapper:
    def __init__(self, model, temperature=0.7):
        self.model = model
        self.temperature = temperature
    
    def invoke(self, messages):
        # Extract text from messages
        if isinstance(messages, list):
            # Handle list of messages
            prompt = "\n".join([msg.content if hasattr(msg, 'content') else str(msg) for msg in messages])
        else:
            prompt = str(messages)
        
        # Generate response
        generation_config = genai.types.GenerationConfig(temperature=self.temperature)
        response = self.model.generate_content(prompt, generation_config=generation_config)
        
        # Return in LangChain format
        class Response:
            def __init__(self, content):
                self.content = content
        
        return Response(response.text)

# Map agents to optimal models
if not gemini_flash_model and not groq_llm:
    raise RuntimeError("❌ No LLM configured! Please set GOOGLE_API_KEY in .env file (local) or Streamlit secrets (cloud)")

llm = groq_llm if groq_llm else GeminiWrapper(gemini_flash_model, 0.7)
strict_llm = GeminiWrapper(gemini_pro_model, 0.3) if gemini_pro_model else GeminiWrapper(gemini_flash_model, 0.3)
vision_llm = GeminiWrapper(gemini_flash_model, 0.7)


class ProfilerAgent:
    """
    Agent 1: The Profiler
    Extracts structured insights from resume and job description.
    Uses entity extraction and semantic comparison.
    """
    
    def __init__(self):
        self.llm = strict_llm
    
    def run(self, state: Dict) -> Dict:
        """
        Analyzes resume vs job description to find strengths/gaps.
        """
        print(f"   📊 ProfilerAgent: Processing resume ({len(state.get('resume_text', ''))} chars)...")
        print(f"   📊 ProfilerAgent: Analyzing job description ({len(state.get('job_description', ''))} chars)...")
        
        prompt = f"""You are an expert talent analyzer. Extract structured insights.

RESUME:
{state['resume_text']}

JOB DESCRIPTION:
{state['job_description']}

Analyze and return JSON with:
1. "matched_skills": List of skills candidate has that match job
2. "missing_skills": Skills mentioned in job but not in resume
3. "strengths": Top 3 strong points
4. "weaknesses": Top 3 areas to probe (vague descriptions, gaps, etc.)
5. "experience_level": "junior", "mid", or "senior"
6. "red_flags": Any concerns (employment gaps, job hopping, etc.)

CRITICAL: Return ONLY valid JSON. No markdown, no code blocks, no explanation. Start with {{ and end with }}.

Example:
{{
  "matched_skills": ["Python", "React"],
  "missing_skills": ["AWS"],
  "strengths": ["Strong experience", "Good leadership", "Clear communication"],
  "weaknesses": ["Cloud knowledge unclear", "No DevOps mentioned"],
  "experience_level": "mid",
  "red_flags": []
}}"""
        
        print(f"   📊 ProfilerAgent: Calling Gemini Flash for analysis...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        print(f"   📊 ProfilerAgent: Received {len(response.content)} chars response")
        
        # Parse JSON response - NO FALLBACKS, BE STRICT
        raw_content = response.content.strip()
        
        # Remove markdown code blocks if present
        if raw_content.startswith('```'):
            lines = raw_content.split('\n')
            raw_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else raw_content
            raw_content = raw_content.replace('```json', '').replace('```', '').strip()
        
        try:
            analysis = json.loads(raw_content)
            print(f"   📊 ProfilerAgent: ✅ Successfully parsed JSON")
        except Exception as e:
            print(f"   ❌ ProfilerAgent: CRITICAL ERROR - JSON parsing failed")
            print(f"   ❌ Error details: {str(e)}")
            print(f"   ❌ Raw response (first 500 chars):\n{raw_content[:500]}")
            raise ValueError(f"ProfilerAgent failed to generate valid JSON. System cannot proceed without candidate profile analysis. LLM output was not valid JSON format.")
        
        state['profile_analysis'] = analysis
        state['agent_reasoning'] = f"📊 Profiler: Found {len(analysis.get('matched_skills', []))} matching skills, identified {len(analysis.get('weaknesses', []))} areas to probe."
        
        return state


class ResearcherAgent:
    """
    Agent 2: The Researcher
    Fetches real-world company data using Tavily search.
    Implements RAG (Retrieval Augmented Generation).
    """
    
    def __init__(self):
        # Try Streamlit secrets first, then .env
        try:
            tavily_key = st.secrets.get("TAVILY_API_KEY")
        except (FileNotFoundError, KeyError, AttributeError):
            tavily_key = os.getenv("TAVILY_API_KEY")
        
        if TAVILY_AVAILABLE and tavily_key and tavily_key != "your_tavily_api_key_here":
            self.tavily_client = TavilyClient(api_key=tavily_key)
        else:
            self.tavily_client = None
        self.llm = strict_llm
    
    def run(self, state: Dict) -> Dict:
        """
        Searches web for company culture, interview style, and recent news.
        """
        company = state.get('company_name', 'the company')
        print(f"   🔍 ResearcherAgent: Researching '{company}'...")
        
        # Skip if Tavily not available
        if not self.tavily_client:
            print(f"   🔍 ResearcherAgent: Tavily not configured, using fallback data")
            state['company_intel'] = f"{company} values innovation, teamwork, and technical excellence. They use modern tech stack and agile methodologies."
            state['agent_reasoning'] = "🔍 Researcher: Using default company profile (Tavily API not configured)"
            return state
        
        try:
            # Search for company culture and interview style
            search_query = f"{company} engineering culture interview process"
            print(f"   🔍 ResearcherAgent: Searching Tavily for '{search_query}'...")
            results = self.tavily_client.search(query=search_query, max_results=3)
            print(f"   🔍 ResearcherAgent: Found {len(results.get('results', []))} results")
            
            # Synthesize findings
            context = "\n\n".join([r.get('content', '') for r in results.get('results', [])])
            print(f"   🔍 ResearcherAgent: Synthesizing {len(context)} chars of data...")
            
            prompt = f"""Summarize key insights about {company} in 3-4 sentences:

SEARCH RESULTS:
{context[:2000]}

Focus on:
- Company culture and values
- Interview style (technical vs behavioral focus)
- Recent news or changes
- What they look for in candidates

Be specific and actionable."""
            
            print(f"   🔍 ResearcherAgent: Calling Gemini Flash to synthesize...")
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state['company_intel'] = response.content
            print(f"   🔍 ResearcherAgent: Generated {len(response.content)} char intel summary")
            state['agent_reasoning'] = f"🔍 Researcher: Found {len(results.get('results', []))} sources on {company}'s interview culture"
            
        except Exception as e:
            print(f"   ⚠️ ResearcherAgent: Search failed ({e}), using fallback")
            state['company_intel'] = f"{company} values innovation and technical excellence."
            state['agent_reasoning'] = f"🔍 Researcher: Using fallback data (Search unavailable)"
        
        return state


class StrategyAgent:
    """
    Strategy Agent: Plans the interview arc
    Decides question sequence based on profile and company intel.
    """
    
    def __init__(self):
        self.llm = strict_llm
    
    def run(self, state: Dict) -> Dict:
        """
        Creates an interview strategy based on candidate profile.
        """
        profile = state.get('profile_analysis', {})
        company_intel = state.get('company_intel', '')
        print(f"   🎯 StrategyAgent: Planning with {len(profile.get('matched_skills', []))} matched skills...")
        print(f"   🎯 StrategyAgent: Considering {len(profile.get('missing_skills', []))} skill gaps...")
        
        prompt = f"""You are designing a realistic interview flow.

CANDIDATE PROFILE:
- Matched Skills: {profile.get('matched_skills', [])}
- Missing Skills: {profile.get('missing_skills', [])}
- Experience Level: {profile.get('experience_level', 'unknown')}
- Weaknesses: {profile.get('weaknesses', [])}

COMPANY CONTEXT:
{company_intel}

Create a strategic interview plan:
1. What persona should the interviewer adopt? (supportive/neutral/challenging)
2. What sequence of topics? (Start easy -> build up OR start with curveball?)
3. Which weaknesses to probe?
4. How many questions per stage?

Return a concise strategy (3-4 sentences)."""
        
        print(f"   🎯 StrategyAgent: Calling Gemini Flash for strategy...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        state['question_strategy'] = response.content
        print(f"   🎯 StrategyAgent: Generated {len(response.content)} char strategy")
        
        # Set initial persona
        if "supportive" in response.content.lower():
            state['interviewer_persona'] = "supportive"
        elif "challenging" in response.content.lower():
            state['interviewer_persona'] = "challenging"
        else:
            state['interviewer_persona'] = "neutral"
        
        print(f"   🎯 StrategyAgent: Set persona to '{state['interviewer_persona']}'")
        state['agent_reasoning'] = f"🎯 Strategy: Planned {state['interviewer_persona']} interview approach"
        
        return state


class InterviewerAgent:
    """
    Agent 3: The Simulation Director
    Conducts interview with dynamic persona injection.
    Adapts questions based on previous answers and feedback.
    """
    
    def __init__(self):
        self.llm = llm
    
    def run(self, state: Dict) -> Dict:
        """
        Generates next interview question based on context and previous feedback.
        """
        stage = state.get('interview_stage', 'intro')
        persona = state.get('interviewer_persona', 'neutral')
        strategy = state.get('question_strategy', '')
        profile = state.get('profile_analysis', {})
        company_intel = state.get('company_intel', '')
        conversation = state.get('conversation_history', [])
        feedback = state.get('feedback_log', [])
        count = state.get('question_count', 0)
        
        print(f"   🎭 InterviewerAgent: Stage={stage}, Persona={persona}, Q#{count+1}")
        print(f"   🎭 InterviewerAgent: {len(conversation)} messages in history")
        
        # Stage-specific instructions - REAL INTERVIEW QUESTIONS
        stage_prompts = {
            "intro": "Ask a targeted opening: 'Walk me through your experience with [KEY_SKILL from JD].' NOT 'tell me about yourself' - that's lazy.",
            "technical": f"""Ask a HARD technical question about: {profile.get('weaknesses', ['their weak area'])[0]}.
Examples:
- 'Explain how you would design [SYSTEM] to handle 10M requests/day.'
- 'What's the time complexity of [ALGORITHM] and why would you choose it over [ALTERNATIVE]?'
- 'Debug this code: [SHOW CODE SNIPPET with bug]'
Make it role-specific for {state.get('company_name', 'this company')}. Expect them to whiteboard/explain in detail.""",
            "behavioral": """Ask a CHALLENGING behavioral question:
- 'Tell me about a time you FAILED on a project. What went wrong?'
- 'Describe a conflict with a coworker. How did you handle it?'
- 'You missed a critical deadline. Walk me through your thought process.'
DEMAND specifics: names, dates, numbers, outcomes. No generic answers.""",
            "closing": "Ask about their weaknesses or gaps: 'You mentioned limited experience with [MISSING_SKILL]. How do you plan to ramp up?' Be direct."
        }
        
        # Persona modifiers - STRICT INTERVIEW STYLE
        persona_tones = {
            "supportive": "Be professional but direct. If they struggle, guide them with leading questions, but don't give away answers.",
            "neutral": "Be like a standard tech interviewer - professional, fact-checking, probing for depth. No fluff.",
            "challenging": "You are a Senior Staff Engineer known for being tough. Be blunt about weak answers. Interrupt vague responses. Demand technical precision."
        }
        
        # Build context from previous answer
        previous_context = ""
        feedback_instruction = ""
        if conversation and len(conversation) >= 2:
            last_q = conversation[-2].content if len(conversation) >= 2 else ""
            last_a = conversation[-1].content if len(conversation) >= 1 else ""
            last_feedback = feedback[-1] if feedback else {}
            last_score = last_feedback.get('score', 0)
            
            previous_context = f"""
PREVIOUS QUESTION: {last_q}
CANDIDATE'S ANSWER: {last_a}
INTERNAL ASSESSMENT: Score {last_score}/10 - {last_feedback.get('tip', '')}
SENTIMENT: {last_feedback.get('sentiment', 'unknown')}
"""
            
            # Adjust follow-up based on performance - BE RUTHLESS
            if last_score <= 2:
                feedback_instruction = f"""
🚨 CRITICAL FAILURE (scored {last_score}/10).
Their answer was unacceptable. React like a REAL interviewer:

IMMEDIATE PUSHBACK:
- "I'm going to stop you there. That's not what I asked."
- "Simply saying '{last_a[:30]}...' doesn't demonstrate the depth we need for this role."
- "Let me rephrase: I need you to walk me through the TECHNICAL DETAILS of how you would..."

DRILL DEEPER:
- "You mentioned [X]. Explain the implementation. What data structures? What's the complexity?"
- "That's too vague. Give me a SPECIFIC example with numbers and outcomes."
- "No, that's incorrect. [Correct them]. Now, knowing that, how would you approach this?"

Don't move on. STAY on this topic until they give substance or admit they don't know."""
            elif last_score < 5:
                feedback_instruction = f"""
⚠️ WEAK ANSWER (scored {last_score}/10).
They're being vague or surface-level. Challenge them:

- "That's a good start, but I need more technical detail. Walk me through the architecture."
- "You said '{last_a[:50]}...' - can you quantify that? What were the metrics? The impact?"
- "I'm not convinced. Give me a concrete example where you personally implemented this."

TEACHING MOMENT: If they're close, give ONE hint: "Think about [CONCEPT]. How does that apply here?"
But don't give away the answer. Make them work for it."""
            elif last_score < 7:
                feedback_instruction = f"""
⚡ MEDIOCRE (scored {last_score}/10).
They answered but without depth. Probe for excellence:

- "Interesting. Now explain the TRADEOFFS. Why did you choose X over Y?"
- "Walk me through a specific edge case in that implementation."
- "How would this scale? What breaks first at 10x load?"

Real senior engineers don't just solve problems - they understand WHY."""
        
        prompt = f"""You are conducting a job interview for {state.get('company_name', 'a company')}.

COMPANY CONTEXT:
{company_intel}

CANDIDATE PROFILE:
- Strengths: {profile.get('strengths', [])}
- Areas to Probe: {profile.get('weaknesses', [])}

INTERVIEW STRATEGY:
{strategy}

CURRENT STAGE: {stage.upper()}
YOUR PERSONA: {persona_tones[persona]}
{stage_prompts.get(stage, 'Continue the conversation naturally.')}

{previous_context}

{feedback_instruction}

INTERVIEWER BEHAVIOR PROTOCOL:
1. **Zero Tolerance for Vagueness**: If they say "I worked on X", interrupt: "HOW did you work on it? What was YOUR contribution?"
2. **The Why Drill**: Every technical choice must be justified. "Why REST over GraphQL?" "Why Redis over Memcached?"
3. **Catch Bullshit**: If they claim expertise but can't explain basics, call it out: "You mentioned 5 years of React, but can't explain hooks. Clarify your actual experience level."
4. **Pressure Testing**: If they give a solution, attack it: "That design fails under [SCENARIO]. How do you handle that?"
5. **Teach Through Failure**: If they're wrong, don't just move on. Correct them: "No, that's incorrect because [REASON]. Now, knowing this, how would you solve it?"
6. **Tone**: Cold, professional, rapid-fire. No "great answer!" Just "Understood. Next question:" or "That's insufficient. Elaborate."

CRITICAL: You are a HIRING MANAGER, not a friendly chatbot. Your job is to FILTER unqualified candidates, not encourage everyone.

Return ONLY the question/statement, no preamble."""
        
        print(f"   🎭 InterviewerAgent: Generating question with {self.llm.__class__.__name__}...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        question = response.content.strip()
        print(f"   🎭 InterviewerAgent: Generated question ({len(question)} chars)")
        
        state['current_question'] = question
        state['conversation_history'] = conversation + [AIMessage(content=question)]
        state['question_count'] = count + 1
        state['agent_reasoning'] = f"🎤 Interviewer: Asking {stage} question (#{count + 1}) in {persona} tone"
        
        return state


class CriticAgent:
    """
    Agent 4: The Shadow Critic
    Silently evaluates answers using STAR method.
    Provides coaching tips without interrupting interview flow.
    """
    
    def __init__(self):
        self.llm = strict_llm
    
    def run(self, state: Dict) -> Dict:
        """
        Analyzes user's answer using STAR framework and provides score.
        """
        question = state.get('current_question', '')
        answer = state.get('current_answer', '')
        stage = state.get('interview_stage', 'intro')
        
        if not answer:
            print(f"   🤔 CriticAgent: No answer to evaluate, skipping...")
            return state
        
        print(f"   🤔 CriticAgent: Evaluating {len(answer)} char answer...")
        
        prompt = f"""You are a silent interview coach evaluating a candidate's answer.

QUESTION: {question}
ANSWER: {answer}

Evaluate using STAR method (Situation, Task, Action, Result):
1. Did they answer the specific question asked?
2. Was the answer structured (STAR for behavioral, clear logic for technical)?
3. Did they show confidence or hesitation?
4. Was it too brief or too rambling?
5. Any red flags? (vague, defensive, off-topic)

BE BRUTALLY HONEST. If answer was weak or didn't address the question, score 1-3. If excellent, score 9-10. Don't be nice.

Return JSON:
{{"score":7,"strengths":"Clear structure","weaknesses":"Missing specific examples","tip":"Use STAR method with concrete metrics","sentiment":"confident"}}

CRITICAL: Return ONLY valid JSON. No markdown blocks, no explanations. Just pure JSON starting with {{."""
        
        print(f"   🤔 CriticAgent: Calling Gemini Flash for evaluation...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        raw_content = response.content.strip()
        
        # Remove markdown code blocks if present
        if raw_content.startswith('```'):
            lines = raw_content.split('\n')
            raw_content = '\n'.join(lines[1:-1]) if len(lines) > 2 else raw_content
            raw_content = raw_content.replace('```json', '').replace('```', '').strip()
        
        try:
            evaluation = json.loads(raw_content)
            print(f"   🤔 CriticAgent: ✅ Successfully parsed evaluation JSON")
        except Exception as e:
            print(f"   ❌ CriticAgent: CRITICAL ERROR - JSON parsing failed")
            print(f"   ❌ Error details: {str(e)}")
            print(f"   ❌ Raw response (first 500 chars):\n{raw_content[:500]}")
            raise ValueError(f"CriticAgent failed to generate valid JSON. Cannot evaluate candidate answer quality without proper scoring.")
        
        state['current_answer_score'] = evaluation.get('score', 0)
        state['coaching_tip'] = evaluation.get('tip', '')
        state['feedback_log'] = state.get('feedback_log', []) + [evaluation]
        print(f"   🤔 CriticAgent: Score={evaluation.get('score')}/10, Sentiment={evaluation.get('sentiment')}")
        state['agent_reasoning'] = f"🤔 Critic: Scored {evaluation['score']}/10 - {evaluation['sentiment']} tone detected"
        
        return state


class ReportAgent:
    """
    Final Report Generator
    Creates comprehensive breakdown of interview performance.
    """
    
    def __init__(self):
        self.llm = strict_llm
    
    def run(self, state: Dict) -> Dict:
        """
        Generates detailed interview performance report.
        """
        print(f"   📊 ReportAgent: Generating final report...")
        
        feedback_log = state.get('feedback_log', [])
        conversation = state.get('conversation_history', [])
        profile = state.get('profile_analysis', {})
        vision_feedback = state.get('vision_feedback_log', [])
        
        avg_score = sum(f.get('score', 0) for f in feedback_log) / max(len(feedback_log), 1)
        print(f"   📊 ReportAgent: Analyzed {len(feedback_log)} answers, avg score={avg_score:.1f}/10")
        print(f"   📊 ReportAgent: {len(conversation)} messages in transcript")
        
        # Build conversation transcript
        transcript = []
        for i, msg in enumerate(conversation):
            role = "Interviewer" if isinstance(msg, AIMessage) else "You"
            transcript.append(f"{role}: {msg.content}")
        
        # Add vision feedback if available
        vision_summary = ""
        if vision_feedback:
            vision_summary = f"\n\nNON-VERBAL ANALYSIS:\n{json.dumps(vision_feedback, indent=2)}"
        
        prompt = f"""Generate a comprehensive interview performance report.

OVERALL SCORE: {avg_score:.1f}/10

CANDIDATE STRENGTHS: {profile.get('strengths', [])}
AREAS TO IMPROVE: {profile.get('weaknesses', [])}

ANSWER-BY-ANSWER FEEDBACK:
{json.dumps(feedback_log, indent=2)}{vision_summary}

Create a report with:
1. **Overall Performance** (1 paragraph)
2. **Top 3 Strengths**
3. **Top 3 Areas for Improvement** 
4. **Specific Action Items** (What to practice for next interview)
5. **Tone & Delivery Assessment**
6. **Non-Verbal Communication** (if video was enabled)

Be constructive but honest."""
        
        print(f"   📊 ReportAgent: Calling Gemini Flash to generate report...")
        response = self.llm.invoke([HumanMessage(content=prompt)])
        print(f"   📊 ReportAgent: Generated {len(response.content)} char report")
        
        report = f"""# 🎯 Interview Performance Report

## Score: {avg_score:.1f}/10

{response.content}

---

## 📊 Detailed Question Analysis

"""
        for i, feedback in enumerate(feedback_log, 1):
            vision_note = ""
            if i <= len(vision_feedback) and vision_feedback[i-1].get('analysis'):
                vision_note = f"\n**Body Language:** {vision_feedback[i-1]['analysis']}"
            
            report += f"""
### Question {i} - Score: {feedback.get('score', 0)}/10
**Strengths:** {feedback.get('strengths', 'N/A')}
**Weaknesses:** {feedback.get('weaknesses', 'N/A')}
**Coaching Tip:** {feedback.get('tip', 'N/A')}{vision_note}

"""
        
        state['final_report'] = report
        state['agent_reasoning'] = f"📋 Report: Generated final assessment (Avg: {avg_score:.1f}/10)"
        
        return state


class VisionCoachAgent:
    """
    NEW: Vision Coach Agent (Multimodal)
    Analyzes body language and non-verbal cues using Gemini's vision capabilities.
    This is the INNOVATION - no DeepFace needed, just send frames to Gemini!
    """
    
    def __init__(self):
        self.llm = vision_llm  # Gemini Flash with multimodal
    
    def analyze_frame(self, image_base64: str, question: str) -> Dict:
        """
        Analyzes a webcam frame for non-verbal cues.
        
        Args:
            image_base64: Base64 encoded image from webcam
            question: The question being answered (for context)
        
        Returns:
            Dict with analysis (confidence, engagement, body_language)
        """
        try:
            prompt = f"""You are an expert interview coach analyzing a candidate's non-verbal communication.

THE QUESTION THEY'RE ANSWERING: {question}

Analyze this webcam image and evaluate:
1. **Confidence Level** (1-10): Eye contact, posture, facial expression
2. **Engagement** (1-10): Attentiveness, energy level
3. **Body Language Signals**: Fidgeting, slouching, hand gestures
4. **Overall Impression**: Professional? Nervous? Prepared?

Return JSON:
{{
    "confidence": 1-10,
    "engagement": 1-10,
    "body_language": "Brief description",
    "coaching_tip": "One specific tip to improve presence"
}}

Return ONLY valid JSON."""
            
            # Create message with image (Gemini multimodal format)
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_base64}"
                    }
                ]
            )
            
            response = self.llm.invoke([message])
            
            # Parse JSON response
            try:
                analysis = json.loads(response.content)
            except:
                analysis = {
                    "confidence": 5,
                    "engagement": 5,
                    "body_language": "Unable to analyze",
                    "coaching_tip": "Maintain eye contact with camera"
                }
            
            return analysis
            
        except Exception as e:
            return {
                "confidence": 0,
                "engagement": 0,
                "body_language": f"Vision analysis unavailable: {str(e)}",
                "coaching_tip": "Enable video for non-verbal feedback"
            }
    
    def run(self, state: Dict) -> Dict:
        """
        Processes video frame if available in state.
        """
        current_frame = state.get('current_video_frame', None)
        current_question = state.get('current_question', '')
        
        if not current_frame:
            state['agent_reasoning'] = "📹 Vision: No video frame available"
            return state
        
        analysis = self.analyze_frame(current_frame, current_question)
        
        # Add to vision feedback log
        vision_log = state.get('vision_feedback_log', [])
        vision_log.append({
            'question_num': state.get('question_count', 0),
            'analysis': analysis.get('body_language', ''),
            'confidence': analysis.get('confidence', 0),
            'engagement': analysis.get('engagement', 0)
        })
        state['vision_feedback_log'] = vision_log
        
        state['current_vision_analysis'] = analysis
        state['agent_reasoning'] = f"📹 Vision: Confidence {analysis['confidence']}/10, Engagement {analysis['engagement']}/10"
        
        return state
