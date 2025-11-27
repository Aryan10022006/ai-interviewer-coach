"""
AI Interview Prep Coach - Multimodal Audio/Video Experience
Adds real-time audio/video capabilities while preserving LangGraph state machine.

ARCHITECTURE:
- Interface Layer: WebRTC + STT + TTS + Vision
- Brain Layer: Unchanged (agents.py, graph.py, state.py)
"""

import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import queue
import pydub
import io
import base64
import time
from PIL import Image
import numpy as np
from typing import Optional, Dict
import threading
from dotenv import load_dotenv
import os

# Import existing brain components (UNCHANGED)
from graph import run_preparation_phase, process_user_answer, generate_final_report
from state import AgentState
from db_manager import create_session, save_qa_step, save_profile, end_session
from pdf_processor import extract_resume_from_pdf

# Audio processing imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Interview Coach - Multimodal",
    page_icon="🎥",
    layout="wide"
)

# ============================================================================
# AUDIO PIPELINE: Speech-to-Text (STT)
# ============================================================================

class AudioTranscriber:
    """Converts speech to text using OpenAI Whisper or Google Speech Recognition"""
    
    def __init__(self, method="whisper"):
        self.method = method
        if method == "whisper" and OPENAI_AVAILABLE:
            openai.api_key = os.getenv("OPENAI_API_KEY")
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
    
    def transcribe_audio_chunk(self, audio_data: bytes) -> str:
        """
        Transcribe audio bytes to text.
        
        Args:
            audio_data: Raw audio bytes (WAV format)
        
        Returns:
            Transcribed text or empty string on error
        """
        try:
            if self.method == "whisper" and OPENAI_AVAILABLE:
                return self._transcribe_whisper(audio_data)
            elif self.method == "google" and SPEECH_RECOGNITION_AVAILABLE:
                return self._transcribe_google(audio_data)
            else:
                return ""
        except Exception as e:
            st.error(f"🎤 Transcription error: {e}")
            return ""
    
    def _transcribe_whisper(self, audio_data: bytes) -> str:
        """Transcribe using OpenAI Whisper API"""
        # Save to temporary file (Whisper requires file input)
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"
        
        response = openai.Audio.transcribe("whisper-1", audio_file)
        return response.get("text", "")
    
    def _transcribe_google(self, audio_data: bytes) -> str:
        """Transcribe using Google Speech Recognition"""
        audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2)
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            st.error(f"Google Speech API error: {e}")
            return ""

# ============================================================================
# AUDIO PIPELINE: Text-to-Speech (TTS)
# ============================================================================

class AudioSynthesizer:
    """Converts text to speech using gTTS, OpenAI TTS, or ElevenLabs"""
    
    def __init__(self, method="gtts"):
        self.method = method
        if method == "openai" and OPENAI_AVAILABLE:
            openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def synthesize_text(self, text: str) -> bytes:
        """
        Convert text to audio bytes.
        
        Args:
            text: Question or feedback from interviewer
        
        Returns:
            Audio bytes (MP3 format)
        """
        try:
            if self.method == "gtts" and GTTS_AVAILABLE:
                return self._synthesize_gtts(text)
            elif self.method == "openai" and OPENAI_AVAILABLE:
                return self._synthesize_openai(text)
            else:
                return b""
        except Exception as e:
            st.error(f"🔊 TTS error: {e}")
            return b""
    
    def _synthesize_gtts(self, text: str) -> bytes:
        """Synthesize using Google Text-to-Speech (free)"""
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    
    def _synthesize_openai(self, text: str) -> bytes:
        """Synthesize using OpenAI TTS API"""
        response = openai.Audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        return response.content

# ============================================================================
# VIDEO PIPELINE: Frame Sampling & Vision Analysis
# ============================================================================

class VideoFrameSampler:
    """Samples video frames at intervals to avoid latency"""
    
    def __init__(self, sample_interval_seconds: float = 3.0):
        self.sample_interval = sample_interval_seconds
        self.last_sample_time = 0
        self.latest_frame = None
        self.confidence_score = 5  # Default neutral
    
    def should_sample_frame(self) -> bool:
        """Check if enough time has passed to sample a new frame"""
        current_time = time.time()
        if current_time - self.last_sample_time >= self.sample_interval:
            self.last_sample_time = current_time
            return True
        return False
    
    def process_frame(self, frame: av.VideoFrame) -> Optional[str]:
        """
        Process video frame and return base64 encoded image if sampling.
        
        Args:
            frame: Video frame from WebRTC
        
        Returns:
            Base64 encoded JPEG or None if not sampling
        """
        if not self.should_sample_frame():
            return None
        
        # Convert frame to PIL Image
        img = frame.to_ndarray(format="rgb24")
        pil_img = Image.fromarray(img)
        
        # Resize for efficiency
        pil_img.thumbnail((640, 480))
        
        # Encode to base64
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        
        self.latest_frame = img_base64
        return img_base64
    
    def analyze_frame_for_confidence(self, frame_base64: str) -> int:
        """
        Placeholder for vision analysis.
        In production, call VisionCoachAgent from agents.py
        
        Args:
            frame_base64: Base64 encoded frame
        
        Returns:
            Confidence score 1-10
        """
        # TODO: Integrate with existing VisionCoachAgent
        # For now, return mock score
        # In real implementation:
        # from agents import VisionCoachAgent
        # vision_coach = VisionCoachAgent()
        # result = vision_coach.analyze({'current_video_frame': frame_base64})
        # return result['confidence_score']
        
        return 7  # Mock score

# ============================================================================
# WEBRTC CALLBACKS
# ============================================================================

class AudioVideoProcessor:
    """Processes WebRTC audio and video streams"""
    
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.video_sampler = VideoFrameSampler(sample_interval_seconds=3.0)
        self.audio_transcriber = AudioTranscriber(method="google")  # Free option
        self.accumulated_audio = []
        self.transcription_buffer = ""
    
    def video_frame_callback(self, frame: av.VideoFrame) -> av.VideoFrame:
        """
        Called for each video frame.
        Sample frames periodically for vision analysis.
        """
        # Sample frame if interval passed
        frame_base64 = self.video_sampler.process_frame(frame)
        
        if frame_base64:
            # Store in session state for LangGraph
            st.session_state.current_video_frame = frame_base64
            
            # Analyze confidence (non-blocking)
            confidence = self.video_sampler.analyze_frame_for_confidence(frame_base64)
            st.session_state.confidence_score = confidence
        
        # Return frame unchanged for display
        return frame
    
    def audio_frame_callback(self, frame: av.AudioFrame) -> av.AudioFrame:
        """
        Called for each audio frame.
        Accumulate audio for transcription.
        """
        # Add frame to queue for processing
        self.audio_queue.put(frame)
        
        # Return frame unchanged
        return frame

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize Streamlit session state for multimodal interview"""
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.mode = 'text'  # 'text' or 'av'
        st.session_state.phase = 'input'  # input, resume_review, interviewing, complete
        st.session_state.state = {}
        st.session_state.messages = []
        
        # Audio/Video specific
        st.session_state.current_video_frame = None
        st.session_state.confidence_score = 5
        st.session_state.audio_buffer = []
        st.session_state.transcription = ""
        st.session_state.is_recording = False
        st.session_state.tts_enabled = True
        
        # Resume analysis
        st.session_state.resume = ""
        st.session_state.job_desc = ""
        st.session_state.company = ""
        st.session_state.candidate_name = ""
        st.session_state.resume_analysis = None

# ============================================================================
# AUDIO PROCESSING THREAD
# ============================================================================

def process_audio_queue(audio_queue: queue.Queue, transcriber: AudioTranscriber):
    """
    Background thread to process audio chunks and transcribe.
    Updates st.session_state.transcription
    """
    audio_chunks = []
    chunk_duration = 2.0  # Process every 2 seconds
    last_process_time = time.time()
    
    while True:
        try:
            # Get audio frame
            frame = audio_queue.get(timeout=0.1)
            audio_chunks.append(frame)
            
            # Check if enough time passed to transcribe
            if time.time() - last_process_time >= chunk_duration:
                if audio_chunks:
                    # Combine chunks
                    combined_audio = combine_audio_frames(audio_chunks)
                    
                    # Transcribe
                    text = transcriber.transcribe_audio_chunk(combined_audio)
                    
                    if text:
                        # Update session state (thread-safe in Streamlit)
                        st.session_state.transcription += " " + text
                    
                    # Reset
                    audio_chunks = []
                    last_process_time = time.time()
        
        except queue.Empty:
            continue
        except Exception as e:
            print(f"Audio processing error: {e}")
            continue

def combine_audio_frames(frames: list) -> bytes:
    """Combine multiple audio frames into single WAV bytes"""
    # This is a simplified version - production code needs proper audio handling
    # TODO: Implement proper frame concatenation
    return b""

# ============================================================================
# PLAY AUDIO (TTS)
# ============================================================================

def play_audio(text: str, synthesizer: AudioSynthesizer):
    """
    Convert text to speech and play in Streamlit.
    
    Args:
        text: Interviewer's question or feedback
        synthesizer: TTS engine
    """
    if not st.session_state.tts_enabled:
        return
    
    with st.spinner("🔊 Generating audio..."):
        audio_bytes = synthesizer.synthesize_text(text)
        
        if audio_bytes:
            # Display audio player
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)

# ============================================================================
# MULTIMODAL INTERVIEW INTERFACE
# ============================================================================

def render_av_mode_interface():
    """Render Live A/V Mode interface with WebRTC"""
    
    st.header("🎥 Live Audio/Video Interview")
    
    # WebRTC Configuration
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    # Create processor
    if 'av_processor' not in st.session_state:
        st.session_state.av_processor = AudioVideoProcessor()
    
    # WebRTC Streamer
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📹 Your Video")
        
        webrtc_ctx = webrtc_streamer(
            key="interview-stream",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            media_stream_constraints={
                "video": {"width": 640, "height": 480},
                "audio": True
            },
            video_frame_callback=st.session_state.av_processor.video_frame_callback,
            audio_frame_callback=st.session_state.av_processor.audio_frame_callback,
            async_processing=True
        )
        
        # Connection status
        if webrtc_ctx.state.playing:
            st.success("✅ Connected - Speak your answer!")
            st.session_state.is_recording = True
        else:
            st.info("📡 Click START to begin")
            st.session_state.is_recording = False
    
    with col2:
        st.subheader("🎯 Real-Time Feedback")
        
        # Confidence score from video analysis
        confidence = st.session_state.confidence_score
        st.metric("Confidence", f"{confidence}/10")
        
        # Progress bars
        st.progress(confidence / 10, text="Body Language")
        
        # Live transcription preview
        st.markdown("**🎤 Live Transcription:**")
        st.text_area(
            "What you're saying...",
            value=st.session_state.transcription,
            height=150,
            disabled=True
        )
        
        # Submit button
        if st.button("✅ Submit Answer", type="primary", disabled=not st.session_state.is_recording):
            if st.session_state.transcription.strip():
                # Pass transcription to LangGraph (UNCHANGED BRAIN)
                process_multimodal_answer(st.session_state.transcription)
                
                # Clear buffer
                st.session_state.transcription = ""
                st.rerun()
            else:
                st.warning("Please speak your answer first!")

def render_text_mode_interface():
    """Render traditional text-based interface (ORIGINAL)"""
    
    st.header("⌨️ Text-Based Interview")
    
    # Display current question
    if st.session_state.state.get('current_question'):
        st.markdown("### 🎤 Interviewer:")
        st.info(st.session_state.state['current_question'])
    
    # Text input
    user_answer = st.text_area(
        "Your Answer:",
        height=200,
        key="text_answer_input"
    )
    
    if st.button("Submit Answer", type="primary"):
        if user_answer.strip():
            # Pass to LangGraph (UNCHANGED)
            result = process_user_answer(st.session_state.state, user_answer)
            st.session_state.state = result
            st.rerun()
        else:
            st.warning("Please type your answer!")

# ============================================================================
# MULTIMODAL ANSWER PROCESSING (Interface Layer)
# ============================================================================

def process_multimodal_answer(transcribed_text: str):
    """
    Process answer from audio/video mode.
    
    This is the INTERFACE LAYER that bridges WebRTC → LangGraph.
    The brain (graph.invoke) doesn't know if input came from text or audio.
    
    Args:
        transcribed_text: Transcribed speech from STT
    """
    
    # Add video frame to state if available
    if st.session_state.current_video_frame:
        st.session_state.state['current_video_frame'] = st.session_state.current_video_frame
        st.session_state.state['video_enabled'] = True
    
    # Add confidence score from vision analysis
    st.session_state.state['confidence_score'] = st.session_state.confidence_score
    
    # Process through LangGraph (UNCHANGED BRAIN)
    result = process_user_answer(st.session_state.state, transcribed_text)
    st.session_state.state = result
    
    # Get next question from state
    next_question = result.get('current_question', '')
    
    # Convert to speech if enabled (TTS)
    if next_question and st.session_state.tts_enabled:
        synthesizer = AudioSynthesizer(method="gtts")
        play_audio(next_question, synthesizer)
    
    # Display in chat history
    st.session_state.messages.append({
        'role': 'user',
        'content': transcribed_text
    })
    st.session_state.messages.append({
        'role': 'assistant',
        'content': next_question
    })

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    init_session_state()
    
    # Title
    st.title("🎯 AI Interview Coach - Multimodal")
    st.markdown("**Switch between Text Mode and Live A/V Mode**")
    
    # Sidebar - Mode Toggle
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Mode selector
        mode = st.radio(
            "Interview Mode:",
            options=['text', 'av'],
            format_func=lambda x: "⌨️ Text Mode" if x == 'text' else "🎥 Live A/V Mode",
            key='mode_selector'
        )
        st.session_state.mode = mode
        
        st.markdown("---")
        
        # Audio settings (for A/V mode)
        if mode == 'av':
            st.subheader("🔊 Audio Settings")
            st.session_state.tts_enabled = st.checkbox("Enable TTS (AI speaks)", value=True)
            
            stt_method = st.selectbox(
                "Speech Recognition:",
                options=["google", "whisper"],
                help="Google is free but less accurate. Whisper is more accurate."
            )
            
            tts_method = st.selectbox(
                "Text-to-Speech:",
                options=["gtts", "openai"],
                help="gTTS is free but robotic. OpenAI TTS is more natural."
            )
            
            st.markdown("---")
            
            st.subheader("📹 Video Settings")
            sample_interval = st.slider(
                "Frame Sample Interval (sec):",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.5,
                help="How often to analyze video frames. Higher = less CPU usage."
            )
        
        st.markdown("---")
        
        # Session info
        if st.session_state.state.get('question_count', 0) > 0:
            st.metric("Questions Asked", st.session_state.state.get('question_count', 0))
            st.metric("Current Stage", st.session_state.state.get('current_stage', 'N/A'))
        
        # API Status
        st.markdown("---")
        st.caption("🔑 API Status:")
        st.caption("✅ Gemini (Google) - Brain")
        st.caption("✅ Groq - Fast Interviewer")
        
        if GTTS_AVAILABLE:
            st.caption("✅ gTTS (Free TTS)")
        
        if SPEECH_RECOGNITION_AVAILABLE:
            st.caption("✅ Google Speech (Free)")
    
    # Main content area
    if st.session_state.phase == 'input':
        render_input_phase()
    
    elif st.session_state.phase == 'resume_review':
        render_resume_review_phase()
    
    elif st.session_state.phase == 'interviewing':
        # Route to appropriate interface based on mode
        if st.session_state.mode == 'av':
            render_av_mode_interface()
        else:
            render_text_mode_interface()
        
        # Display chat history below
        render_chat_history()
    
    elif st.session_state.phase == 'complete':
        render_complete_phase()

# ============================================================================
# PHASE RENDERERS (Simplified - delegate to existing app.py logic)
# ============================================================================

def render_input_phase():
    """Render input collection phase"""
    st.header("📋 Interview Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.candidate_name = st.text_input("Your Name:", "John Doe")
        st.session_state.company = st.text_input("Target Company:", "Microsoft")
    
    with col2:
        st.session_state.job_desc = st.text_area("Job Description:", height=150)
    
    # Resume input - text or PDF
    st.subheader("📄 Your Resume")
    resume_input_method = st.radio("Input Method:", ["Paste Text", "Upload PDF"], horizontal=True)
    
    if resume_input_method == "Paste Text":
        st.session_state.resume = st.text_area("Paste Resume:", height=200)
    else:
        uploaded_file = st.file_uploader("Upload Resume PDF:", type=['pdf'])
        if uploaded_file:
            # Extract text from PDF (same as app.py)
            extracted_text = extract_resume_from_pdf(uploaded_file)
            if extracted_text:
                st.session_state.resume = extracted_text
                st.success(f"✅ Extracted {len(extracted_text)} characters from PDF")
            else:
                st.error("❌ Failed to extract text from PDF")
    
    if st.button("Start Interview", type="primary"):
        if all([st.session_state.resume, st.session_state.job_desc, st.session_state.company]):
            # Run preparation phase (UNCHANGED BRAIN)
            with st.spinner("🧠 Analyzing your profile..."):
                # Create initial state dict (same structure as app.py)
                session_id = create_session(
                    candidate_name=st.session_state.candidate_name,
                    company=st.session_state.company,
                    role="Engineering Role",
                    resume_length=len(st.session_state.resume)
                )
                
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
                
                # Run preparation with state dict
                result = run_preparation_phase(initial_state)
                
                st.session_state.state = result
                st.session_state.phase = 'interviewing'
                st.session_state.messages = [
                    {"role": "assistant", "content": result.get('current_question', 'Let\'s begin!')}
                ]
                st.rerun()
        else:
            st.error("Please fill in all fields!")

def render_resume_review_phase():
    """Placeholder for resume review"""
    st.info("Resume review phase - TODO")
    if st.button("Continue to Interview"):
        st.session_state.phase = 'interviewing'
        st.rerun()

def render_chat_history():
    """Display conversation history"""
    st.markdown("---")
    st.subheader("💬 Conversation History")
    
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Interviewer:** {msg['content']}")

def render_complete_phase():
    """Display final report"""
    st.success("✅ Interview Complete!")
    
    # Generate report (UNCHANGED BRAIN)
    report = generate_final_report(st.session_state.state)
    st.markdown(report)
    
    if st.button("Start New Interview"):
        # Reset
        st.session_state.clear()
        st.rerun()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
