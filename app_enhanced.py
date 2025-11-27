"""
AI Interview Prep Coach - Enhanced Streamlit UI with Video Support
Uses FREE APIs: Gemini (multimodal vision) + Groq (fast interviewer)
"""

import streamlit as st
from dotenv import load_dotenv
import os
import cv2
import base64
from PIL import Image
import io
import time

from graph import run_preparation_phase, process_user_answer, generate_final_report
from state import AgentState

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Interview Prep Coach (FREE)",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.phase = 'input'  # input, analyzing, interviewing, complete
    st.session_state.state = {}
    st.session_state.messages = []
    st.session_state.video_enabled = False
    st.session_state.last_frame = None


def capture_webcam_frame():
    """Capture a single frame from webcam and return base64 encoded image"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL Image
            img = Image.fromarray(frame_rgb)
            # Resize for efficiency
            img.thumbnail((640, 480))
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return img_base64
        return None
    except Exception as e:
        st.sidebar.warning(f"📹 Camera access failed: {e}")
        return None


def initialize_interview():
    """
    Runs the preparation phase (Profiler → Researcher → Strategy → First Question)
    """
    with st.spinner("🤖 Agents are analyzing your profile (using FREE Gemini + Groq APIs)..."):
        # Create initial state
        initial_state = {
            'resume_text': st.session_state.resume,
            'job_description': st.session_state.job_desc,
            'company_name': st.session_state.company,
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
            'coaching_tip': '',
            'video_enabled': st.session_state.video_enabled,
            'current_video_frame': '',
            'current_vision_analysis': {},
            'vision_feedback_log': []
        }
        
        # Run preparation
        result = run_preparation_phase(initial_state)
        
        st.session_state.state = result
        st.session_state.phase = 'interviewing'
        st.session_state.messages = [
            {"role": "assistant", "content": result.get('current_question', 'Let\'s begin!')}
        ]
        st.session_state.initialized = True


# Header
st.title("🎯 AI Interview Prep Coach")
st.markdown("**Multi-Agent Interview Simulator with FREE APIs (Gemini + Groq) & Live Video Analysis**")

# Sidebar - Agent Reasoning Dashboard
with st.sidebar:
    st.header("🧠 Live Agent Thoughts")
    st.markdown("*Powered by Google Gemini & Groq (100% FREE)*")
    
    if st.session_state.phase == 'interviewing' or st.session_state.phase == 'complete':
        state = st.session_state.state
        
        # Current agent action
        st.info(state.get('agent_reasoning', 'Waiting for input...'))
        
        # Interview progress
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Questions", state.get('question_count', 0))
        with col2:
            st.metric("Stage", state.get('interview_stage', 'N/A').upper())
        
        st.metric("Persona", state.get('interviewer_persona', 'N/A').title())
        
        # Vision analysis (if enabled)
        if state.get('video_enabled') and state.get('current_vision_analysis'):
            st.markdown("---")
            st.markdown("### 📹 Live Body Language")
            vision = state['current_vision_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Confidence", f"{vision.get('confidence', 0)}/10")
            with col2:
                st.metric("Engagement", f"{vision.get('engagement', 0)}/10")
            
            st.caption(f"💡 {vision.get('coaching_tip', 'N/A')}")
        
        # Profile analysis
        with st.expander("📊 Profile Analysis"):
            profile = state.get('profile_analysis', {})
            st.write("**Matched Skills:**", ', '.join(profile.get('matched_skills', [])))
            st.write("**Missing Skills:**", ', '.join(profile.get('missing_skills', [])))
            st.write("**Weaknesses to Probe:**")
            for w in profile.get('weaknesses', []):
                st.write(f"- {w}")
        
        # Last answer score (Shadow Critic)
        if state.get('feedback_log'):
            last_feedback = state['feedback_log'][-1]
            st.metric("Last Answer Score", f"{last_feedback.get('score', 0)}/10")
            st.caption(f"💡 Tip: {last_feedback.get('tip', 'N/A')}")
    else:
        st.caption("Agent insights will appear here during the interview.")
        st.markdown("---")
        st.markdown("### 🆓 Using FREE APIs")
        st.success("✅ Google Gemini (Vision + Analysis)")
        st.success("✅ Groq (Ultra-fast Llama 3.3)")
        st.info("No credit card required!")

# Main content
if st.session_state.phase == 'input':
    st.header("📝 Setup Your Interview")
    
    # API Key Check
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not google_key or google_key == "your_google_api_key_here":
        st.error("⚠️ Google API Key not found! Get your FREE key:")
        st.code("1. Visit: https://makersuite.google.com/app/apikey\n2. Create free account\n3. Copy API key\n4. Add to .env file: GOOGLE_API_KEY=your_key")
        st.stop()
    
    if not groq_key or groq_key == "your_groq_api_key_here":
        st.warning("⚠️ Groq API Key not found (optional but recommended for speed)")
        st.code("1. Visit: https://console.groq.com/keys\n2. Sign up (free)\n3. Copy API key\n4. Add to .env file: GROQ_API_KEY=your_key")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Resume")
        resume = st.text_area(
            "Paste your resume or key highlights",
            height=200,
            placeholder="e.g., Software Engineer with 3 years experience in Python, Django, React..."
        )
    
    with col2:
        st.subheader("Job Description")
        job_desc = st.text_area(
            "Paste the job description",
            height=200,
            placeholder="e.g., Looking for Senior Backend Engineer with experience in..."
        )
    
    company = st.text_input(
        "Company Name (for context)",
        placeholder="e.g., Google, Microsoft, Startup XYZ"
    )
    
    st.markdown("---")
    
    # Video option
    st.subheader("🎥 Enable Video Analysis (Optional)")
    video_enabled = st.checkbox(
        "📹 Use webcam for body language analysis (powered by Gemini Vision)",
        help="Gemini will analyze your confidence, posture, and engagement in real-time - 100% FREE!"
    )
    
    if video_enabled:
        st.info("💡 Make sure your webcam is connected and browser allows camera access")
    
    st.markdown("---")
    
    if st.button("🚀 Start Interview", type="primary", use_container_width=True):
        if resume and job_desc and company:
            st.session_state.resume = resume
            st.session_state.job_desc = job_desc
            st.session_state.company = company
            st.session_state.video_enabled = video_enabled
            initialize_interview()
            st.rerun()
        else:
            st.error("⚠️ Please fill in all fields before starting.")

elif st.session_state.phase == 'interviewing':
    st.header("💬 Interview in Progress")
    
    # Video preview (if enabled)
    if st.session_state.state.get('video_enabled'):
        col1, col2 = st.columns([3, 1])
        with col2:
            st.markdown("### 📹 Live Camera")
            video_placeholder = st.empty()
            
            # Capture frame button
            if st.button("📸 Capture Frame", help="Capture current frame for analysis"):
                frame = capture_webcam_frame()
                if frame:
                    st.session_state.last_frame = frame
                    st.success("✅ Frame captured!")
    
    # Display conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # User input
    user_answer = st.chat_input("Type your answer here...")
    
    if user_answer:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_answer})
        
        # Capture video frame if enabled
        if st.session_state.state.get('video_enabled'):
            frame = capture_webcam_frame()
            if frame:
                st.session_state.state['current_video_frame'] = frame
        
        with st.spinner("🤖 AI analyzing your answer (Gemini + Groq working together)..."):
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
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🏁 End Interview", use_container_width=True):
            st.session_state.phase = 'complete'
            st.rerun()

elif st.session_state.phase == 'complete':
    st.header("📊 Interview Performance Report")
    
    # Generate report if not already done
    if 'final_report' not in st.session_state.state:
        with st.spinner("📝 Generating comprehensive report (powered by Gemini Pro)..."):
            result = generate_final_report(st.session_state.state)
            st.session_state.state = result
    
    # Display report
    report = st.session_state.state.get('final_report', 'Report generation failed.')
    st.markdown(report)
    
    # Show video analysis summary if available
    if st.session_state.state.get('vision_feedback_log'):
        st.markdown("---")
        st.markdown("## 🎥 Video Analysis Summary")
        
        vision_log = st.session_state.state['vision_feedback_log']
        avg_confidence = sum(v.get('confidence', 0) for v in vision_log) / max(len(vision_log), 1)
        avg_engagement = sum(v.get('engagement', 0) for v in vision_log) / max(len(vision_log), 1)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Confidence", f"{avg_confidence:.1f}/10")
        with col2:
            st.metric("Average Engagement", f"{avg_engagement:.1f}/10")
        
        st.markdown("### Question-by-Question Body Language")
        for i, v in enumerate(vision_log, 1):
            st.write(f"**Q{i}:** {v.get('analysis', 'N/A')}")
    
    # Download button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name="interview_report.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Interview", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# Footer
st.markdown("---")
st.caption("🤖 Powered by FREE APIs: Google Gemini 2.0 Flash (Vision) + Groq Llama 3.3 (Speed) | No Credit Card Required!")
