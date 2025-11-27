"""
AI Interview Prep Coach - Shared State Definition
This module defines the state structure that flows through all agents.
"""

from typing import TypedDict, List, Dict, Literal
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Central state object passed between all agents in the graph.
    This is the "brain" of the system - all agents read and write to this.
    """
    # Input Phase
    resume_text: str
    job_description: str
    company_name: str
    
    # Research Phase
    company_intel: str  # Live data from web search
    profile_analysis: Dict[str, any]  # Skills, strengths, weaknesses, gaps
    
    # Interview Strategy
    interview_stage: Literal["intro", "technical", "behavioral", "closing", "complete"]
    interviewer_persona: str  # "supportive", "neutral", "challenging"
    question_strategy: str  # Plan from strategy agent
    
    # Conversation Loop
    conversation_history: List[BaseMessage]
    current_question: str
    current_answer: str
    
    # Shadow Critic (Hidden scoring)
    feedback_log: List[Dict[str, any]]  # Real-time evaluations
    current_answer_score: int  # 1-10 scale
    coaching_tip: str
    
    # Vision Analysis (NEW - Multimodal)
    video_enabled: bool  # Whether webcam is active
    current_video_frame: str  # Base64 encoded frame
    current_vision_analysis: Dict[str, any]  # Gemini's body language analysis
    vision_feedback_log: List[Dict[str, any]]  # Non-verbal tracking
    
    # Meta
    question_count: int
    agent_reasoning: str  # For UI transparency - shows what agent is thinking
