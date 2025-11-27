"""
AI Interview Prep Coach - LangGraph Orchestrator
This is the "brain" - coordinates all agents in a state machine.
Implements conditional edges for dynamic interview flow.
"""

from typing import Dict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from state import AgentState
from agents import (
    ProfilerAgent,
    ResearcherAgent, 
    StrategyAgent,
    InterviewerAgent,
    CriticAgent,
    ReportAgent,
    VisionCoachAgent
)
from db_manager import save_qa_step, save_profile, end_session


# Initialize all agents
profiler = ProfilerAgent()
researcher = ResearcherAgent()
strategist = StrategyAgent()
interviewer = InterviewerAgent()
critic = CriticAgent()
reporter = ReportAgent()
vision_coach = VisionCoachAgent()


# Node functions (wrap agent execution)
def profile_node(state: Dict) -> Dict:
    """Analyze resume and job description"""
    return profiler.run(state)


def research_node(state: Dict) -> Dict:
    """Fetch company intel from web"""
    return researcher.run(state)


def strategy_node(state: Dict) -> Dict:
    """Plan interview approach"""
    return strategist.run(state)


def interview_node(state: Dict) -> Dict:
    """Ask next question"""
    return interviewer.run(state)


def critique_node(state: Dict) -> Dict:
    """Evaluate user's answer silently and persist to database"""
    result = critic.run(state)
    
    # Save to database if session exists
    if 'session_id' in state and state.get('current_question') and state.get('current_answer'):
        try:
            feedback = state.get('feedback_log', [])[-1] if state.get('feedback_log') else {}
            save_qa_step(
                session_id=state['session_id'],
                question_number=state.get('question_count', 0),
                stage=state.get('interview_stage', 'unknown'),
                question=state.get('current_question', ''),
                answer=state.get('current_answer', ''),
                feedback=feedback
            )
            print(f"   💾 Saved Q&A to database (session {state['session_id']})")
        except Exception as e:
            print(f"   ⚠️ Database save failed: {e}")
    
    return result


def report_node(state: Dict) -> Dict:
    """Generate final report"""
    return reporter.run(state)


def pushback_node(state: Dict) -> Dict:
    """
    PUSHBACK MODE: Don't ask a new question.
    Instead, aggressively rephrase the SAME question demanding more depth.
    This is triggered when the candidate gives a weak/vague answer (score <= 2).
    """
    print(f"\n   ⚡ PUSHBACK NODE: Demanding better answer to previous question")
    
    last_question = state.get('current_question', '')
    last_answer = state.get('current_answer', '')
    last_feedback = state.get('feedback_log', [])[-1] if state.get('feedback_log') else {}
    
    # Create an aggressive follow-up prompt
    pushback_prompt = f"""You asked: "{last_question}"

The candidate responded: "{last_answer}"

This answer scored {last_feedback.get('score', 0)}/10 because: {last_feedback.get('weaknesses', 'it lacked depth and specifics')}.

You are a tough senior engineer. You CANNOT accept this weak answer. Respond like a real interviewer would:

EXAMPLE PUSHBACKS:
- "I'm going to stop you there. That answer is too vague for a [LEVEL] role. Let me be specific: [REPHRASE with technical details required]"
- "You mentioned [X] but didn't explain HOW. Walk me through the actual implementation - what data structures, algorithms, trade-offs?"
- "That's a surface-level answer. Give me a CONCRETE example: project name, your role, the problem, your solution, and measurable outcomes."
- "No, I need technical depth. Explain the [CONCEPT] behind [THEIR_CLAIM]. What's the complexity? Edge cases?"

BE STERN. Make them realize this is a real interview, not a casual chat.

Return ONLY your pushback statement/question."""
    
    # Use interviewer agent to generate pushback
    pushback_state = state.copy()
    pushback_state['conversation_history'] = pushback_state.get('conversation_history', []) + [
        HumanMessage(content=pushback_prompt)
    ]
    
    # Generate the pushback question
    result = interviewer.run(pushback_state)
    
    # Don't increment question counter (same question, different phrasing)
    result['question_count'] = state.get('question_count', 0)
    
    return result


# Conditional edge logic
def should_continue_interview(state: Dict) -> Literal["pushback", "interview", "report"]:
    """
    Decide next step based on candidate performance:
    - pushback: Answer was too weak, drill deeper (don't move to next question)
    - interview: Continue to next question
    - report: End interview and generate final report
    """
    question_count = state.get('question_count', 0)
    stage = state.get('interview_stage', 'intro')
    feedback_log = state.get('feedback_log', [])
    
    # Check termination conditions first
    if question_count >= 10 or stage == "complete":
        return "report"
    
    # PUSHBACK LOGIC: If last answer was critically weak, don't move on
    if feedback_log and question_count > 0:
        last_score = feedback_log[-1].get('score', 0)
        pushback_count = state.get('pushback_count', 0)
        
        # Scores 1-2: Demand better answer (but max 2 attempts per question)
        if last_score <= 2 and pushback_count < 2:
            print(f"\n   🚨 PUSHBACK: Answer scored {last_score}/10 - demanding elaboration (attempt {pushback_count + 1}/2)")
            state['pushback_count'] = pushback_count + 1
            return "pushback"
        
        # If they failed after 2 pushbacks, move on but note the failure
        if pushback_count >= 2:
            print(f"\n   ❌ TOPIC FAILED: Moving to next question after {pushback_count} failed attempts")
            state['pushback_count'] = 0
            state['failed_topics'] = state.get('failed_topics', []) + [state.get('current_question', '')[:50]]
    
    # Early termination: 3+ consistently poor answers
    if len(feedback_log) >= 3:
        recent_scores = [f.get('score', 0) for f in feedback_log[-3:]]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        if avg_recent < 3.5:
            state['interview_stage'] = 'complete'
            state['early_termination_reason'] = f'Performance below bar (avg {avg_recent:.1f}/10)'
            print(f"\n   🛑 EARLY TERMINATION: Consistently weak performance")
            return "report"
    
    return "interview"


def advance_stage(state: Dict) -> Dict:
    """
    Progress interview through stages based on question count AND performance.
    Fails candidates early if they're clearly not qualified.
    """
    count = state.get('question_count', 0)
    feedback_log = state.get('feedback_log', [])
    
    # Calculate average score if we have feedback
    if len(feedback_log) >= 2:
        avg_score = sum(f.get('score', 0) for f in feedback_log) / len(feedback_log)
        
        # STRICT: End interview early if candidate is clearly failing
        if avg_score < 4 and count >= 3:
            state['interview_stage'] = 'complete'
            state['early_termination_reason'] = f'Performance too low (avg {avg_score:.1f}/10 after {count} questions)'
            print(f"\n   ⚠️ EARLY TERMINATION: Candidate avg score {avg_score:.1f}/10 - Not meeting bar")
            return state
    
    # Normal progression
    if count <= 2:
        state['interview_stage'] = 'intro'
    elif count <= 5:
        state['interview_stage'] = 'technical'
    elif count <= 7:
        state['interview_stage'] = 'behavioral'
    elif count == 8:
        state['interview_stage'] = 'closing'
    else:
        state['interview_stage'] = 'complete'
    
    return state


def stage_transition_node(state: Dict) -> Dict:
    """Helper node to advance stages"""
    return advance_stage(state)


# Build the graph
def create_interview_graph():
    """
    Creates the LangGraph state machine.
    
    Flow:
    1. Profile + Research (parallel prep)
    2. Strategy planning
    3. Interview Loop: Ask -> User Answers -> Critique -> Next Question
    4. Final Report
    """
    
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("profile", profile_node)
    workflow.add_node("research", research_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("interview", interview_node)
    workflow.add_node("critique", critique_node)
    workflow.add_node("pushback", pushback_node)  # NEW: Aggressive follow-up node
    workflow.add_node("stage_check", stage_transition_node)
    workflow.add_node("report", report_node)
    
    # Define edges (workflow sequence)
    workflow.set_entry_point("profile")
    
    # Preparation phase
    workflow.add_edge("profile", "research")
    workflow.add_edge("research", "strategy")
    workflow.add_edge("strategy", "interview")
    
    # Interview loop (this is the magic)
    # After asking question, we wait for user input (handled by Streamlit)
    # Then critique is called, which feeds back to interview
    workflow.add_edge("interview", "critique")
    workflow.add_edge("critique", "stage_check")
    
    # Conditional: Continue, pushback, or finish?
    workflow.add_conditional_edges(
        "stage_check",
        should_continue_interview,
        {
            "pushback": "pushback",    # Answer too weak, drill deeper
            "interview": "interview",  # Loop back for next question
            "report": "report"         # Generate final report
        }
    )
    
    # Pushback also goes to critique (to re-evaluate the new answer)
    workflow.add_edge("pushback", "critique")
    
    workflow.add_edge("report", END)
    
    return workflow.compile()


# Helper function for step-by-step execution
def run_preparation_phase(state: Dict) -> Dict:
    """
    Runs the initial analysis before starting interview.
    This executes: Profile -> Research -> Strategy -> First Question
    """
    print("\n" + "="*60)
    print("🚀 STARTING PREPARATION PHASE")
    print("="*60)
    
    # Run agents sequentially (no graph to avoid loops)
    print("\n📊 Step 1: Running Profiler Agent...")
    state = profiler.run(state)
    print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
    
    print("\n🔍 Step 2: Running Researcher Agent...")
    state = researcher.run(state)
    print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
    
    print("\n🎯 Step 3: Running Strategy Agent...")
    state = strategist.run(state)
    print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
    
    print("\n🎤 Step 4: Generating First Question...")
    state = interviewer.run(state)
    print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
    print(f"   Question: {state.get('current_question', 'N/A')[:100]}...")
    
    print("\n" + "="*60)
    print("✅ PREPARATION COMPLETE")
    print("="*60 + "\n")
    
    return state


def process_user_answer(state: Dict, user_answer: str) -> Dict:
    """
    Processes user's answer and generates next question.
    This executes: Vision (if enabled) -> Critique -> Stage Check -> Interview
    """
    print("\n" + "="*60)
    print(f"💬 PROCESSING ANSWER #{state.get('question_count', 0) + 1}")
    print("="*60)
    
    # Add user answer to state
    state['current_answer'] = user_answer
    state['conversation_history'] = state.get('conversation_history', []) + [
        HumanMessage(content=user_answer)
    ]
    
    # Run vision analysis if video enabled and frame available
    if state.get('video_enabled') and state.get('current_video_frame'):
        print("\n📹 Running Vision Coach...")
        state = vision_coach.run(state)
        print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
    
    # Run critique
    print("\n🤔 Running Critic Agent...")
    state = critic.run(state)
    print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
    print(f"   Score: {state.get('current_answer_score', 0)}/10")
    
    # Check stage progression
    state = advance_stage(state)
    print(f"\n📈 Stage: {state.get('interview_stage', 'N/A').upper()}")
    
    # Decide next action
    decision = should_continue_interview(state)
    print(f"🎯 Decision: {decision.upper()}")
    
    if decision == "interview":
        print("\n🎤 Generating Next Question...")
        state = interviewer.run(state)
        print(f"   ✅ {state.get('agent_reasoning', 'Done')}")
        print(f"   Question: {state.get('current_question', 'N/A')[:100]}...")
    else:
        print("\n📊 Generating Final Report...")
        state = reporter.run(state)
        state['interview_stage'] = 'complete'
        print(f"   ✅ Report generated")
    
    print("="*60 + "\n")
    
    return state


def generate_final_report(state: Dict) -> Dict:
    """
    Generates comprehensive interview report.
    """
    return reporter.run(state)
