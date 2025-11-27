"""
Test script to demonstrate logging functionality.
Shows which agent is doing what during interview preparation.
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Import agents
from agents import (
    profiler, researcher, strategist, interviewer, 
    critic, reporter
)

print("\n" + "="*70)
print(" "*20 + "LOGGING TEST SUITE")
print("="*70 + "\n")

# Test data
test_state = {
    'resume_text': """John Doe
Senior Software Engineer
5 years experience in Python, JavaScript, React, and Node.js
Built scalable microservices handling 1M+ requests/day
Led team of 3 engineers on e-commerce platform
Strong problem-solving and communication skills""",
    
    'job_description': """Senior Backend Engineer at TechCorp
We're looking for a skilled backend engineer with:
- 4+ years Python experience
- Knowledge of distributed systems
- Experience with AWS/GCP
- Strong algorithmic thinking
- Team leadership experience""",
    
    'company_name': 'TechCorp',
    'interview_stage': 'intro',
    'conversation_history': [],
    'feedback_log': [],
    'question_count': 0
}

print("📝 Test Data Prepared:")
print(f"   Resume: {len(test_state['resume_text'])} characters")
print(f"   Job Description: {len(test_state['job_description'])} characters")
print(f"   Company: {test_state['company_name']}")
print("\n" + "="*70 + "\n")

# Test 1: Profiler Agent
print("🧪 TEST 1: PROFILER AGENT")
print("-"*70)
try:
    result = profiler.run(test_state.copy())
    print(f"\n✅ Profiler completed successfully")
    print(f"   Matched Skills: {result.get('profile_analysis', {}).get('matched_skills', [])}")
    print(f"   Missing Skills: {result.get('profile_analysis', {}).get('missing_skills', [])}")
    print(f"   Experience Level: {result.get('profile_analysis', {}).get('experience_level', 'N/A')}")
except Exception as e:
    print(f"\n❌ Profiler failed: {e}")

print("\n" + "="*70 + "\n")

# Test 2: Researcher Agent
print("🧪 TEST 2: RESEARCHER AGENT")
print("-"*70)
try:
    result = researcher.run(test_state.copy())
    print(f"\n✅ Researcher completed successfully")
    print(f"   Company Intel: {result.get('company_intel', 'N/A')[:200]}...")
except Exception as e:
    print(f"\n❌ Researcher failed: {e}")

print("\n" + "="*70 + "\n")

# Test 3: Strategy Agent
print("🧪 TEST 3: STRATEGY AGENT")
print("-"*70)
try:
    # Need profile first
    state_with_profile = profiler.run(test_state.copy())
    state_with_research = researcher.run(state_with_profile)
    result = strategist.run(state_with_research)
    print(f"\n✅ Strategy completed successfully")
    print(f"   Persona: {result.get('interviewer_persona', 'N/A')}")
    print(f"   Strategy: {result.get('question_strategy', 'N/A')[:200]}...")
except Exception as e:
    print(f"\n❌ Strategy failed: {e}")

print("\n" + "="*70 + "\n")

# Test 4: Interviewer Agent
print("🧪 TEST 4: INTERVIEWER AGENT")
print("-"*70)
try:
    # Need full preparation first
    state_prep = profiler.run(test_state.copy())
    state_prep = researcher.run(state_prep)
    state_prep = strategist.run(state_prep)
    result = interviewer.run(state_prep)
    print(f"\n✅ Interviewer completed successfully")
    print(f"   Question: {result.get('current_question', 'N/A')}")
    print(f"   Question Count: {result.get('question_count', 0)}")
except Exception as e:
    print(f"\n❌ Interviewer failed: {e}")

print("\n" + "="*70 + "\n")

# Test 5: Critic Agent
print("🧪 TEST 5: CRITIC AGENT")
print("-"*70)
try:
    # Create state with question and answer
    state_with_qa = test_state.copy()
    state_with_qa['current_question'] = "Tell me about your experience with Python."
    state_with_qa['current_answer'] = """I have 5 years of experience with Python. 
I've built microservices using Flask and FastAPI, worked with databases like PostgreSQL, 
and used async programming for high-throughput systems. In my last role, I optimized 
our API to handle 1M+ requests per day by implementing caching and connection pooling."""
    
    result = critic.run(state_with_qa)
    print(f"\n✅ Critic completed successfully")
    print(f"   Score: {result.get('current_answer_score', 'N/A')}/10")
    print(f"   Tip: {result.get('coaching_tip', 'N/A')}")
    if result.get('feedback_log'):
        feedback = result['feedback_log'][0]
        print(f"   Strengths: {feedback.get('strengths', 'N/A')}")
        print(f"   Weaknesses: {feedback.get('weaknesses', 'N/A')}")
        print(f"   Sentiment: {feedback.get('sentiment', 'N/A')}")
except Exception as e:
    print(f"\n❌ Critic failed: {e}")

print("\n" + "="*70 + "\n")

# Test 6: Report Agent
print("🧪 TEST 6: REPORT AGENT")
print("-"*70)
try:
    # Create state with feedback
    state_with_feedback = test_state.copy()
    state_with_feedback['profile_analysis'] = {
        'matched_skills': ['Python', 'Leadership'],
        'missing_skills': ['AWS'],
        'strengths': ['Experience', 'Problem-solving', 'Team lead'],
        'weaknesses': ['Cloud knowledge']
    }
    state_with_feedback['feedback_log'] = [
        {'score': 8, 'strengths': 'Detailed', 'weaknesses': 'Could mention AWS', 'tip': 'Add cloud examples', 'sentiment': 'confident'},
        {'score': 7, 'strengths': 'Good structure', 'weaknesses': 'Vague on metrics', 'tip': 'Use numbers', 'sentiment': 'confident'},
        {'score': 6, 'strengths': 'Honest', 'weaknesses': 'Too brief', 'tip': 'Elaborate more', 'sentiment': 'nervous'}
    ]
    state_with_feedback['conversation_history'] = []
    
    result = reporter.run(state_with_feedback)
    print(f"\n✅ Reporter completed successfully")
    print(f"   Report length: {len(result.get('final_report', ''))} characters")
    print(f"\n   Report preview:")
    print(f"   {result.get('final_report', 'N/A')[:300]}...")
except Exception as e:
    print(f"\n❌ Reporter failed: {e}")

print("\n" + "="*70)
print(" "*15 + "ALL TESTS COMPLETED")
print("="*70 + "\n")

print("📊 SUMMARY:")
print("   - Logging shows which agent is executing")
print("   - Character counts track data flow")
print("   - LLM calls are visible")
print("   - Errors show fallback behavior")
print("\n✅ Check the output above to see detailed agent logging!")
