"""
Interview Session History Viewer
View past interview sessions with full transcript and analysis.
"""

import streamlit as st
import sqlite3
from datetime import datetime
import json
from typing import Dict, List

DB_PATH = 'interview_sessions.db'

def get_all_sessions() -> List[Dict]:
    """Get all interview sessions sorted by date."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''SELECT id, candidate_name, company, role, start_time, end_time, 
                     overall_score, total_questions, early_termination, final_verdict
                     FROM sessions 
                     ORDER BY start_time DESC''')
        
        sessions = c.fetchall()
        conn.close()
        
        return [
            {
                'id': s[0],
                'name': s[1],
                'company': s[2],
                'role': s[3],
                'start_time': s[4],
                'end_time': s[5],
                'score': s[6],
                'questions': s[7],
                'early_termination': s[8],
                'verdict': s[9]
            }
            for s in sessions
        ]
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return []

def get_session_details(session_id: int) -> Dict:
    """Get full details for a specific session."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Session info
    c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = c.fetchone()
    
    # QA logs
    c.execute('''SELECT question_number, stage, question, answer, answer_length,
                 critic_score, critic_strengths, critic_weaknesses, critic_tip, 
                 sentiment, timestamp
                 FROM qa_logs WHERE session_id = ? ORDER BY question_number''', 
              (session_id,))
    qa_logs = c.fetchall()
    
    # Profile analysis
    c.execute('SELECT * FROM profile_analysis WHERE session_id = ?', (session_id,))
    profile = c.fetchone()
    
    conn.close()
    
    return {
        'session': session,
        'qa_logs': qa_logs,
        'profile': profile
    }

def display_session_card(session: Dict):
    """Display a session as a card in the list."""
    # Determine status emoji
    if session['early_termination']:
        status_emoji = "🚫"
        status_text = "Terminated Early"
    elif session['score'] is None:
        status_emoji = "⏸️"
        status_text = "In Progress"
    elif session['score'] >= 7:
        status_emoji = "🌟"
        status_text = "Strong Performance"
    elif session['score'] >= 5:
        status_emoji = "✅"
        status_text = "Passed"
    else:
        status_emoji = "❌"
        status_text = "Needs Improvement"
    
    # Format date
    try:
        start_dt = datetime.fromisoformat(session['start_time'])
        date_str = start_dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        date_str = session['start_time']
    
    # Score display
    score_str = f"{session['score']:.1f}/10" if session['score'] else "N/A"
    
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            st.markdown(f"### {status_emoji} {session['name']}")
            st.markdown(f"**{session['company']}** - {session['role']}")
            st.caption(f"📅 {date_str}")
        
        with col2:
            st.metric("Score", score_str)
            st.caption(f"📝 {session['questions']} questions")
        
        with col3:
            if st.button("View Details", key=f"view_{session['id']}"):
                st.session_state.selected_session = session['id']
                st.rerun()
        
        st.markdown("---")

def display_qa_log(qa_log, index: int):
    """Display a single Q&A interaction."""
    question_num, stage, question, answer, answer_len, score, strengths, weaknesses, tip, sentiment, timestamp = qa_log
    
    # Score emoji
    if score >= 7:
        score_emoji = "🌟"
    elif score >= 5:
        score_emoji = "✅"
    elif score >= 3:
        score_emoji = "⚠️"
    else:
        score_emoji = "❌"
    
    with st.expander(f"Question {question_num}: {stage.upper()} Stage - Score: {score_emoji} {score}/10", expanded=(index == 0)):
        st.markdown(f"**Interviewer:** {question}")
        
        st.markdown("**Your Answer:**")
        st.info(answer if answer else "_[No answer recorded]_")
        st.caption(f"📏 Answer length: {answer_len} characters")
        
        if strengths:
            st.markdown("**✅ Strengths:**")
            st.success(strengths)
        
        if weaknesses:
            st.markdown("**❌ Weaknesses:**")
            st.error(weaknesses)
        
        if tip:
            st.markdown("**💡 Improvement Tip:**")
            st.warning(tip)
        
        if sentiment:
            st.caption(f"🎭 Sentiment: {sentiment}")

def main():
    st.set_page_config(page_title="Interview Session History", page_icon="📚", layout="wide")
    
    st.title("📚 Interview Session History")
    st.markdown("Review your past interviews, see what worked, and track improvement over time.")
    
    # Initialize session state
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = None
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        if st.button("🏠 Back to All Sessions"):
            st.session_state.selected_session = None
            st.rerun()
        
        st.markdown("---")
        
        filter_company = st.text_input("Filter by Company", "")
        filter_min_score = st.slider("Minimum Score", 0.0, 10.0, 0.0, 0.5)
        
        show_terminated = st.checkbox("Show Early Terminations", True)
        show_incomplete = st.checkbox("Show Incomplete", True)
    
    # Main content
    if st.session_state.selected_session is None:
        # List view
        st.header("All Interview Sessions")
        
        sessions = get_all_sessions()
        
        if not sessions:
            st.info("📭 No interview sessions found. Complete an interview to see history here!")
            return
        
        # Apply filters
        filtered = sessions
        if filter_company:
            filtered = [s for s in filtered if filter_company.lower() in s['company'].lower()]
        if filter_min_score > 0:
            filtered = [s for s in filtered if s['score'] and s['score'] >= filter_min_score]
        if not show_terminated:
            filtered = [s for s in filtered if not s['early_termination']]
        if not show_incomplete:
            filtered = [s for s in filtered if s['score'] is not None]
        
        st.caption(f"Showing {len(filtered)} of {len(sessions)} sessions")
        
        # Display sessions
        for session in filtered:
            display_session_card(session)
    
    else:
        # Detail view
        session_id = st.session_state.selected_session
        details = get_session_details(session_id)
        
        if not details['session']:
            st.error("❌ Session not found")
            return
        
        session = details['session']
        qa_logs = details['qa_logs']
        profile = details['profile']
        
        # Session header
        st.header(f"Session #{session_id}: {session[1]}")  # candidate_name
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Company", session[2])  # company
        with col2:
            st.metric("Role", session[3])  # role
        with col3:
            score = session[6] if session[6] else 0
            st.metric("Overall Score", f"{score:.1f}/10")
        with col4:
            st.metric("Questions", session[9])  # total_questions
        
        # Early termination warning
        if session[10]:  # early_termination
            st.error(f"🚫 **Interview Terminated Early:** {session[10]}")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Q&A Transcript", "👤 Profile Analysis", "📊 Stats", "🔍 Raw Data"])
        
        with tab1:
            st.subheader("Interview Transcript")
            
            if not qa_logs:
                st.info("No Q&A logs found")
            else:
                for idx, qa_log in enumerate(qa_logs):
                    display_qa_log(qa_log, idx)
        
        with tab2:
            st.subheader("Candidate Profile Analysis")
            
            if not profile:
                st.info("No profile analysis found")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### ✅ Matched Skills")
                    matched = json.loads(profile[1]) if profile[1] else []
                    if matched:
                        for skill in matched:
                            st.success(f"✓ {skill}")
                    else:
                        st.caption("_None recorded_")
                    
                    st.markdown("### 💪 Strengths")
                    strengths = json.loads(profile[3]) if profile[3] else []
                    if strengths:
                        for strength in strengths:
                            st.info(f"• {strength}")
                    else:
                        st.caption("_None recorded_")
                
                with col2:
                    st.markdown("### ❌ Missing Skills")
                    missing = json.loads(profile[2]) if profile[2] else []
                    if missing:
                        for skill in missing:
                            st.error(f"✗ {skill}")
                    else:
                        st.caption("_None recorded_")
                    
                    st.markdown("### ⚠️ Weaknesses")
                    weaknesses = json.loads(profile[4]) if profile[4] else []
                    if weaknesses:
                        for weakness in weaknesses:
                            st.warning(f"• {weakness}")
                    else:
                        st.caption("_None recorded_")
                
                if profile[5]:  # experience_level
                    st.markdown(f"**Experience Level:** {profile[5]}")
                
                if profile[6]:  # red_flags
                    red_flags = json.loads(profile[6])
                    if red_flags:
                        st.markdown("### 🚩 Red Flags")
                        for flag in red_flags:
                            st.error(f"🚩 {flag}")
        
        with tab3:
            st.subheader("Performance Statistics")
            
            if qa_logs:
                scores = [qa[5] for qa in qa_logs]  # critic_score
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Score", f"{avg_score:.1f}/10")
                with col2:
                    st.metric("Best Question", f"{max_score:.1f}/10")
                with col3:
                    st.metric("Worst Question", f"{min_score:.1f}/10")
                
                # Score distribution
                st.markdown("### Score Distribution")
                import pandas as pd
                df = pd.DataFrame({
                    'Question': [f"Q{qa[0]}" for qa in qa_logs],
                    'Score': [qa[5] for qa in qa_logs],
                    'Stage': [qa[1] for qa in qa_logs]
                })
                st.bar_chart(df.set_index('Question')['Score'])
                
                # Stage breakdown
                st.markdown("### Performance by Stage")
                stages = {}
                for qa in qa_logs:
                    stage = qa[1]
                    score = qa[5]
                    if stage not in stages:
                        stages[stage] = []
                    stages[stage].append(score)
                
                for stage, scores in stages.items():
                    avg = sum(scores) / len(scores)
                    st.metric(f"{stage.upper()} Stage", f"{avg:.1f}/10", f"{len(scores)} questions")
        
        with tab4:
            st.subheader("Raw Session Data")
            st.json({
                'session_id': session[0],
                'candidate_name': session[1],
                'company': session[2],
                'role': session[3],
                'start_time': session[4],
                'end_time': session[5],
                'overall_score': session[6],
                'final_verdict': session[7],
                'resume_length': session[8],
                'total_questions': session[9],
                'early_termination': session[10]
            })

if __name__ == "__main__":
    main()
