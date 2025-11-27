"""
Quick test script to verify all agents work correctly.
Run this before launching the full Streamlit app.
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("🔍 Testing AI Interview Prep Coach Components (FREE API Version)\n")
print("=" * 50)

# Test 1: Check API Keys
print("\n1. Checking API Keys...")
google_key = os.getenv("GOOGLE_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if google_key and google_key != "your_google_api_key_here":
    print("   ✅ Google API key found (Gemini)")
else:
    print("   ❌ Google API key missing - REQUIRED")
    print("   Get FREE key at: https://makersuite.google.com/app/apikey")
    print("   Set GOOGLE_API_KEY in .env file")

if groq_key and groq_key != "your_groq_api_key_here":
    print("   ✅ Groq API key found (Fast Llama 3.3)")
else:
    print("   ⚠️  Groq API key missing - RECOMMENDED for speed")
    print("   Get FREE key at: https://console.groq.com/keys")

if tavily_key and tavily_key != "your_tavily_api_key_here":
    print("   ✅ Tavily API key found")
else:
    print("   ⚠️  Tavily API key missing - System will use fallback data")

# Test 2: Import all modules
print("\n2. Testing Module Imports...")
try:
    from state import AgentState
    print("   ✅ state.py imported")
except Exception as e:
    print(f"   ❌ state.py failed: {e}")

try:
    from agents import ProfilerAgent, ResearcherAgent, StrategyAgent, InterviewerAgent, CriticAgent, ReportAgent
    print("   ✅ agents.py imported")
except Exception as e:
    print(f"   ❌ agents.py failed: {e}")

try:
    from graph import create_interview_graph, run_preparation_phase
    print("   ✅ graph.py imported")
except Exception as e:
    print(f"   ❌ graph.py failed: {e}")

# Test 3: Quick agent test
print("\n3. Testing Agent Functionality...")
try:
    test_state = {
        'resume_text': 'Software Engineer with 3 years Python experience',
        'job_description': 'Looking for Senior Python Developer with FastAPI',
        'company_name': 'TechCorp',
        'interview_stage': 'intro',
        'conversation_history': [],
        'feedback_log': [],
        'question_count': 0,
        'agent_reasoning': '',
        'profile_analysis': {},
        'company_intel': '',
        'question_strategy': '',
        'interviewer_persona': 'neutral',
        'current_question': '',
        'current_answer': '',
        'current_answer_score': 0,
        'coaching_tip': ''
    }
    
    from agents import ProfilerAgent
    profiler = ProfilerAgent()
    result = profiler.run(test_state)
    
    if result.get('profile_analysis'):
        print("   ✅ Profiler Agent working")
        print(f"      Found {len(result['profile_analysis'].get('matched_skills', []))} matched skills")
    else:
        print("   ⚠️  Profiler returned empty analysis")
        
except Exception as e:
    print(f"   ❌ Agent test failed: {e}")

# Test 4: Check dependencies
print("\n4. Checking Dependencies...")
try:
    import langchain
    print("   ✅ langchain installed")
except:
    print("   ❌ langchain missing - run: pip install langchain")

try:
    import langgraph
    print("   ✅ langgraph installed")
except:
    print("   ❌ langgraph missing - run: pip install langgraph")

try:
    import streamlit
    print("   ✅ streamlit installed")
except:
    print("   ❌ streamlit missing - run: pip install streamlit")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("   ✅ langchain-google-genai installed (Gemini)")
except:
    print("   ❌ langchain-google-genai missing - run: pip install langchain-google-genai")

try:
    from langchain_groq import ChatGroq
    print("   ✅ langchain-groq installed (Fast Llama)")
except:
    print("   ⚠️  langchain-groq missing - run: pip install langchain-groq")

try:
    import cv2
    print("   ✅ opencv-python installed (webcam)")
except:
    print("   ⚠️  opencv-python missing - run: pip install opencv-python")

print("\n" + "=" * 50)
print("\n✨ Test Complete!")
print("\n🚀 To run the app:")
print("\n   Basic version (no video):")
print("   streamlit run app.py")
print("\n   Enhanced version (with video analysis):")
print("   streamlit run app_enhanced.py")
print("\n🔧 To fix any issues:")
print("   pip install -r requirements.txt")
print("   Get FREE API keys:")
print("     - Google Gemini: https://makersuite.google.com/app/apikey")
print("     - Groq: https://console.groq.com/keys")
print("   Add keys to .env file")
