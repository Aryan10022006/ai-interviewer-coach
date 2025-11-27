"""
Database Manager for Interview Sessions
Persists all interview data, scores, and analysis for later review.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os

DB_PATH = 'interview_sessions.db'

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Sessions table - one row per interview
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  candidate_name TEXT,
                  company TEXT,
                  role TEXT,
                  start_time TEXT,
                  end_time TEXT,
                  overall_score REAL,
                  final_verdict TEXT,
                  resume_length INTEGER,
                  total_questions INTEGER,
                  early_termination TEXT)''')
    
    # Question-Answer logs - detailed transcript
    c.execute('''CREATE TABLE IF NOT EXISTS qa_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id INTEGER,
                  question_number INTEGER,
                  stage TEXT,
                  question TEXT,
                  answer TEXT,
                  answer_length INTEGER,
                  critic_score REAL,
                  critic_strengths TEXT,
                  critic_weaknesses TEXT,
                  critic_tip TEXT,
                  sentiment TEXT,
                  timestamp TEXT,
                  FOREIGN KEY(session_id) REFERENCES sessions(id))''')
    
    # Profile analysis - what the system learned about the candidate
    c.execute('''CREATE TABLE IF NOT EXISTS profile_analysis
                 (session_id INTEGER PRIMARY KEY,
                  matched_skills TEXT,
                  missing_skills TEXT,
                  strengths TEXT,
                  weaknesses TEXT,
                  experience_level TEXT,
                  red_flags TEXT,
                  FOREIGN KEY(session_id) REFERENCES sessions(id))''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_session(candidate_name: str, company: str, role: str, resume_length: int) -> int:
    """Create a new interview session and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    start_time = datetime.now().isoformat()
    
    c.execute('''INSERT INTO sessions 
                 (candidate_name, company, role, start_time, resume_length, total_questions)
                 VALUES (?, ?, ?, ?, ?, 0)''',
              (candidate_name, company, role, start_time, resume_length))
    
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    
    print(f"📝 Created session ID: {session_id} for {candidate_name}")
    return session_id

def save_qa_step(session_id: int, question_number: int, stage: str, 
                 question: str, answer: str, feedback: Dict):
    """Save a single question-answer interaction."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''INSERT INTO qa_logs 
                 (session_id, question_number, stage, question, answer, answer_length,
                  critic_score, critic_strengths, critic_weaknesses, critic_tip, sentiment, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (session_id, question_number, stage, question, answer, len(answer),
               feedback.get('score', 0),
               feedback.get('strengths', ''),
               feedback.get('weaknesses', ''),
               feedback.get('tip', ''),
               feedback.get('sentiment', ''),
               datetime.now().isoformat()))
    
    # Update total questions in session
    c.execute('UPDATE sessions SET total_questions = ? WHERE id = ?',
              (question_number, session_id))
    
    conn.commit()
    conn.close()

def save_profile(session_id: int, profile: Dict):
    """Save the candidate profile analysis."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''INSERT OR REPLACE INTO profile_analysis 
                 (session_id, matched_skills, missing_skills, strengths, weaknesses, 
                  experience_level, red_flags)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (session_id,
               json.dumps(profile.get('matched_skills', [])),
               json.dumps(profile.get('missing_skills', [])),
               json.dumps(profile.get('strengths', [])),
               json.dumps(profile.get('weaknesses', [])),
               profile.get('experience_level', ''),
               json.dumps(profile.get('red_flags', []))))
    
    conn.commit()
    conn.close()

def end_session(session_id: int, overall_score: float, verdict: str, 
                early_termination: Optional[str] = None):
    """Mark session as complete with final scores."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    end_time = datetime.now().isoformat()
    
    c.execute('''UPDATE sessions 
                 SET end_time = ?, overall_score = ?, final_verdict = ?, early_termination = ?
                 WHERE id = ?''',
              (end_time, overall_score, verdict, early_termination, session_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Session {session_id} ended - Score: {overall_score}/10")

def get_session_stats(session_id: int) -> Dict:
    """Get statistics for a session."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get session info
    c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = c.fetchone()
    
    # Get all QA logs
    c.execute('SELECT * FROM qa_logs WHERE session_id = ? ORDER BY question_number', 
              (session_id,))
    qa_logs = c.fetchall()
    
    # Get profile
    c.execute('SELECT * FROM profile_analysis WHERE session_id = ?', (session_id,))
    profile = c.fetchone()
    
    conn.close()
    
    return {
        'session': session,
        'qa_logs': qa_logs,
        'profile': profile
    }

def get_recent_sessions(limit: int = 10) -> List[Dict]:
    """Get most recent interview sessions."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''SELECT id, candidate_name, company, role, start_time, overall_score, total_questions
                 FROM sessions 
                 ORDER BY start_time DESC 
                 LIMIT ?''', (limit,))
    
    sessions = c.fetchall()
    conn.close()
    
    return [
        {
            'id': s[0],
            'name': s[1],
            'company': s[2],
            'role': s[3],
            'date': s[4],
            'score': s[5],
            'questions': s[6]
        }
        for s in sessions
    ]

# Initialize DB on import
if not os.path.exists(DB_PATH):
    init_db()
