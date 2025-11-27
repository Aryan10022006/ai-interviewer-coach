"""
AI Interview Prep Coach - Streamlit UI
Interactive interface with live agent reasoning visualization.
This is the "Wow Factor" - users see how AI is judging them in real-time.
"""

import streamlit as st
from dotenv import load_dotenv
import os

from graph import run_preparation_phase, process_user_answer, generate_final_report
from state import AgentState
from pdf_processor import extract_resume_from_pdf
from db_manager import create_session, save_profile, end_session
from resume_analyzer import create_resume_analyzer

# Load environment variables
load_dotenv()

# Initialize resume analyzer
resume_analyzer = create_resume_analyzer()

# Page configuration
st.set_page_config(
    page_title="AI Interview Prep Coach",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.phase = 'input'  # input, resume_review, analyzing, interviewing, complete
    st.session_state.state = {}
    st.session_state.messages = []
    st.session_state.resume_analysis = None


def initialize_interview():
    """
    Runs the preparation phase (Profiler -> Researcher -> Strategy -> First Question)
    """
    with st.spinner("🤖 Agents are analyzing your profile..."):
        # Create database session
        session_id = create_session(
            candidate_name="Anonymous",
            company=st.session_state.company,
            role="Engineering Role",
            resume_length=len(st.session_state.resume)
        )
        
        # Create initial state
        initial_state = {
            'session_id': session_id,
            'resume_text': st.session_state.resume,
            'job_description': st.session_state.job_desc,
            'company_name': st.session_state.company,
            'interview_stage': 'intro',
            'conversation_history': [],
            'feedback_log': [],
            'question_count': 0,
            'pushback_count': 0,
            'failed_topics': [],
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
        
        # Run preparation
        result = run_preparation_phase(initial_state)
        
        # Save profile to database
        if result.get('profile_analysis'):
            save_profile(session_id, result['profile_analysis'])
        
        st.session_state.state = result
        st.session_state.phase = 'interviewing'
        st.session_state.messages = [
            {"role": "assistant", "content": result.get('current_question', 'Let\'s begin!')}
        ]
        st.session_state.initialized = True


# Header
st.title("🎯 AI Interview Prep Coach")
st.markdown("**Multi-Agent Interview Simulator with Real-Time AI Analysis**")

# Sidebar - Agent Reasoning Dashboard
with st.sidebar:
    st.header("🧠 Live Agent Thoughts")
    st.markdown("*See what the AI is thinking in real-time*")
    
    if st.session_state.phase == 'interviewing' or st.session_state.phase == 'complete':
        state = st.session_state.state
        
        # Current agent action
        st.info(state.get('agent_reasoning', 'Waiting for input...'))
        
        # Interview progress
        st.metric("Questions Asked", state.get('question_count', 0))
        st.metric("Current Stage", state.get('interview_stage', 'N/A').upper())
        st.metric("Interviewer Persona", state.get('interviewer_persona', 'N/A').title())
        
        # Profile analysis
        with st.expander("📊 Profile Analysis"):
            profile = state.get('profile_analysis', {})
            st.write("**Matched Skills:**", ', '.join(profile.get('matched_skills', [])))
            st.write("**Missing Skills:**", ', '.join(profile.get('missing_skills', [])))
            st.write("**Weaknesses to Probe:**")
            for w in profile.get('weaknesses', []):
                st.write(f"- {w}")
        
        # Last answer score + Live Coaching
        if state.get('feedback_log'):
            last_feedback = state['feedback_log'][-1]
            last_score = last_feedback.get('score', 0)
            
            st.metric("Last Answer Score", f"{last_score}/10")
            
            # Live coaching based on performance
            st.markdown("---")
            st.subheader("💡 Live Coach")
            
            if last_score <= 2:
                st.error("🚨 **CRITICAL: Answer too weak!**")
                st.warning(f"**Problem:** {last_feedback.get('weaknesses', 'Too vague, no depth')}")
                st.info(f"**Fix it:** {last_feedback.get('tip', 'Use specific examples with numbers and outcomes')}")
                st.markdown("**Framework to use:**\n- **S**ituation: Set the context\n- **T**ask: Your responsibility\n- **A**ction: What YOU did (not the team)\n- **R**esult: Measurable impact")
            elif last_score < 5:
                st.warning("⚠️ **Weak answer - needs more depth**")
                st.info(f"💡 {last_feedback.get('tip', 'Add specific examples')}")
                st.caption(f"Weakness: {last_feedback.get('weaknesses', 'N/A')}")
            elif last_score < 7:
                st.success(f"✅ **Good, but could be better**")
                st.info(f"💡 {last_feedback.get('tip', 'N/A')}")
            else:
                st.success(f"🌟 **Excellent answer!**")
                st.caption(f"Strength: {last_feedback.get('strengths', 'Well structured')}")
            
            # Show pushback status
            pushback_count = state.get('pushback_count', 0)
            if pushback_count > 0:
                st.error(f"⚡ **PUSHBACK MODE** - Attempt {pushback_count}/2")
                st.caption("Interviewer is demanding more depth on this question!")
    else:
        st.caption("Agent insights will appear here during the interview.")

# Main content
if st.session_state.phase == 'input':
    st.header("📝 Setup Your Interview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Resume")
        
        # Upload method selector
        upload_method = st.radio(
            "Choose input method:",
            ["📄 Upload PDF", "✏️ Paste Text"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        resume = ""
        if upload_method == "📄 Upload PDF":
            uploaded_file = st.file_uploader(
                "Upload your resume (PDF)",
                type=['pdf'],
                help="Upload a PDF resume. We'll extract the text automatically."
            )
            
            if uploaded_file:
                try:
                    with st.spinner("📄 Extracting text from PDF..."):
                        resume = extract_resume_from_pdf(uploaded_file, validate=True)
                    
                    st.success(f"✅ Extracted {len(resume)} characters from PDF")
                    
                    # Show preview
                    with st.expander("📋 Preview extracted text"):
                        st.text(resume[:500] + "..." if len(resume) > 500 else resume)
                    
                except Exception as e:
                    st.error(f"❌ PDF extraction failed: {str(e)}")
                    st.info("💡 Try pasting your resume text manually instead.")
        else:
            resume = st.text_area(
                "Paste your resume or key highlights",
                height=200,
                placeholder="e.g., Software Engineer with 3 years experience in Python, Django, React...",
                key="resume_text_area"
            )
    
    with col2:
        st.subheader("Job Description")
        job_desc = st.text_area(
            "Paste the job description",
            height=200,
            placeholder="e.g., Looking for Senior Backend Engineer with experience in...",
            key="job_desc_area"
        )
    
    company = st.text_input(
        "Company Name (for context)",
        placeholder="e.g., Google, Microsoft, Startup XYZ"
    )
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📄 Analyze Resume First", use_container_width=True):
            if resume:
                st.session_state.resume = resume
                st.session_state.job_desc = job_desc
                st.session_state.company = company
                st.session_state.phase = 'resume_review'
                st.rerun()
            else:
                st.error("⚠️ Please provide your resume first.")
    
    with col_btn2:
        if st.button("🚀 Start Interview Directly", type="primary", use_container_width=True):
            if resume and job_desc and company:
                st.session_state.resume = resume
                st.session_state.job_desc = job_desc
                st.session_state.company = company
                
                try:
                    initialize_interview()
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Interview initialization failed: {str(e)}")
                    st.info("💡 This usually means the AI couldn't generate proper analysis. Check your resume and job description are detailed enough.")
            else:
                st.error("⚠️ Please fill in all fields before starting.")

elif st.session_state.phase == 'resume_review':
    st.header("📄 Resume Analysis Report")
    
    # Run analysis if not done yet
    if st.session_state.resume_analysis is None:
        with st.spinner("🔍 Analyzing your resume with brutal honesty..."):
            if resume_analyzer:
                # Pass company name for company-specific fit analysis
                analysis = resume_analyzer.analyze(
                    st.session_state.resume,
                    st.session_state.job_desc,
                    st.session_state.company  # NEW: Pass company for researcher agent
                )
                st.session_state.resume_analysis = analysis
                
                # Generate and display report
                report = resume_analyzer.generate_report(analysis)
                st.markdown(report)
            else:
                st.error("❌ Resume analyzer not available")
                st.session_state.phase = 'input'
                st.rerun()
    else:
        # Display cached analysis
        report = resume_analyzer.generate_report(st.session_state.resume_analysis)
        st.markdown(report)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Edit Resume", use_container_width=True):
            st.session_state.phase = 'input'
            st.session_state.resume_analysis = None
            st.rerun()
    
    with col2:
        if st.button("✅ Proceed to Interview", type="primary", use_container_width=True):
            try:
                initialize_interview()
                st.rerun()
            except ValueError as e:
                st.error(f"❌ Interview initialization failed: {str(e)}")
                st.info("💡 This usually means the AI couldn't generate proper analysis. Check your resume and job description are detailed enough.")

elif st.session_state.phase == 'interviewing':
    st.header("💬 Interview in Progress")
    
    # Display conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # User input
    user_answer = st.chat_input("Type your answer here...")
    
    if user_answer:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_answer})
        
        with st.spinner("🤔 AI is evaluating your answer..."):
            # Process answer and get next question
            result = process_user_answer(st.session_state.state, user_answer)
            st.session_state.state = result
            
            # Check if interview is complete
            if result.get('interview_stage') == 'complete':
                st.session_state.phase = 'complete'
            else:
                # Add next question
                next_question = result.get('current_question', '')
                if next_question:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": next_question
                    })
        
        st.rerun()
    
    # Manual end button
    if st.button("🏁 End Interview & Get Report"):
        st.session_state.phase = 'complete'
        st.rerun()

elif st.session_state.phase == 'complete':
    st.header("📊 Interview Performance Report")
    
    # Generate report if not already done
    if 'final_report' not in st.session_state.state:
        with st.spinner("📝 Generating comprehensive report..."):
            result = generate_final_report(st.session_state.state)
            st.session_state.state = result
    
    # Display report
    report = st.session_state.state.get('final_report', 'Report generation failed.')
    st.markdown(report)
    
    # Download button
    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name="interview_report.md",
        mime="text/markdown"
    )
    
    # Reset button
    if st.button("🔄 Start New Interview"):
        st.session_state.clear()
        st.rerun()


# Footer
st.markdown("---")
st.caption("🤖 Powered by Multi-Agent LangGraph Architecture | Built with GPT-4 & Tavily")
