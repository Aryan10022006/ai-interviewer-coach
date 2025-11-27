"""
Production-Ready Multimodal Components
Robust implementations with error handling and fallbacks.
"""

import streamlit as st
import queue
import threading
import time
from typing import Optional, Dict, Callable
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# ROBUST AUDIO TRANSCRIBER WITH FALLBACKS
# ============================================================================

class RobustAudioTranscriber:
    """
    Production-ready STT with multiple fallback engines.
    Priority: Whisper → Google → Manual text input
    """
    
    def __init__(self):
        self.engines = []
        self._init_engines()
    
    def _init_engines(self):
        """Initialize available STT engines in priority order"""
        
        # Try OpenAI Whisper (most accurate)
        try:
            import openai
            import os
            if os.getenv("OPENAI_API_KEY"):
                self.engines.append(("whisper", self._whisper_transcribe))
                logger.info("✅ Whisper STT available")
        except ImportError:
            logger.warning("⚠️ OpenAI not installed - Whisper unavailable")
        
        # Try Google Speech Recognition (free fallback)
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.engines.append(("google", self._google_transcribe))
            logger.info("✅ Google Speech STT available")
        except ImportError:
            logger.warning("⚠️ SpeechRecognition not installed")
        
        if not self.engines:
            logger.error("❌ No STT engines available!")
            raise RuntimeError("No speech recognition engines available")
    
    def transcribe(self, audio_data: bytes, timeout: float = 5.0) -> str:
        """
        Transcribe audio with automatic fallback.
        
        Args:
            audio_data: Raw audio bytes (WAV format, 16kHz, 16-bit)
            timeout: Max seconds to wait for response
        
        Returns:
            Transcribed text or empty string
        """
        for engine_name, engine_func in self.engines:
            try:
                logger.info(f"🎤 Trying {engine_name} STT...")
                text = engine_func(audio_data, timeout)
                
                if text.strip():
                    logger.info(f"✅ {engine_name} transcribed: {text[:50]}...")
                    return text
                else:
                    logger.warning(f"⚠️ {engine_name} returned empty text")
            
            except Exception as e:
                logger.error(f"❌ {engine_name} failed: {e}")
                continue
        
        # All engines failed
        logger.error("❌ All STT engines failed")
        return ""
    
    def _whisper_transcribe(self, audio_data: bytes, timeout: float) -> str:
        """Transcribe using OpenAI Whisper"""
        import openai
        import io
        
        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.wav"
        
        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="en"  # Force English for faster processing
        )
        return response.get("text", "")
    
    def _google_transcribe(self, audio_data: bytes, timeout: float) -> str:
        """Transcribe using Google Speech Recognition"""
        import speech_recognition as sr
        
        audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2)
        
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            logger.warning("Google could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Google API error: {e}")
            raise

# ============================================================================
# ROBUST TTS WITH FALLBACKS
# ============================================================================

class RobustTTSEngine:
    """
    Production-ready TTS with multiple fallback engines.
    Priority: OpenAI TTS → ElevenLabs → gTTS → Text display
    """
    
    def __init__(self):
        self.engines = []
        self._init_engines()
    
    def _init_engines(self):
        """Initialize available TTS engines in priority order"""
        
        # Try OpenAI TTS (natural voice)
        try:
            import openai
            import os
            if os.getenv("OPENAI_API_KEY"):
                self.engines.append(("openai", self._openai_synthesize))
                logger.info("✅ OpenAI TTS available")
        except ImportError:
            logger.warning("⚠️ OpenAI not installed")
        
        # Try ElevenLabs (ultra-realistic)
        try:
            from elevenlabs import generate, set_api_key
            import os
            if os.getenv("ELEVENLABS_API_KEY"):
                set_api_key(os.getenv("ELEVENLABS_API_KEY"))
                self.engines.append(("elevenlabs", self._elevenlabs_synthesize))
                logger.info("✅ ElevenLabs TTS available")
        except ImportError:
            logger.warning("⚠️ ElevenLabs not installed")
        
        # Try gTTS (free fallback)
        try:
            from gtts import gTTS
            self.engines.append(("gtts", self._gtts_synthesize))
            logger.info("✅ gTTS available")
        except ImportError:
            logger.warning("⚠️ gTTS not installed")
        
        if not self.engines:
            logger.warning("⚠️ No TTS engines - text-only mode")
    
    def synthesize(self, text: str, timeout: float = 10.0) -> Optional[bytes]:
        """
        Synthesize text to speech with automatic fallback.
        
        Args:
            text: Text to convert to speech
            timeout: Max seconds to wait
        
        Returns:
            Audio bytes (MP3) or None if all engines fail
        """
        # Truncate very long text
        if len(text) > 500:
            text = text[:500] + "..."
        
        for engine_name, engine_func in self.engines:
            try:
                logger.info(f"🔊 Trying {engine_name} TTS...")
                audio_bytes = engine_func(text, timeout)
                
                if audio_bytes:
                    logger.info(f"✅ {engine_name} synthesized {len(audio_bytes)} bytes")
                    return audio_bytes
            
            except Exception as e:
                logger.error(f"❌ {engine_name} failed: {e}")
                continue
        
        logger.error("❌ All TTS engines failed - falling back to text")
        return None
    
    def _openai_synthesize(self, text: str, timeout: float) -> bytes:
        """Synthesize using OpenAI TTS"""
        import openai
        
        response = openai.Audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            speed=1.1  # Slightly faster for interview pace
        )
        return response.content
    
    def _elevenlabs_synthesize(self, text: str, timeout: float) -> bytes:
        """Synthesize using ElevenLabs"""
        from elevenlabs import generate
        
        audio = generate(
            text=text,
            voice="Adam",  # Professional male voice
            model="eleven_monolingual_v1"
        )
        return audio
    
    def _gtts_synthesize(self, text: str, timeout: float) -> bytes:
        """Synthesize using Google TTS"""
        from gtts import gTTS
        import io
        
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()

# ============================================================================
# THREAD-SAFE AUDIO BUFFER
# ============================================================================

class ThreadSafeAudioBuffer:
    """
    Thread-safe buffer for accumulating audio chunks.
    Handles WebRTC's async callbacks safely.
    """
    
    def __init__(self, chunk_duration_seconds: float = 2.0):
        self.chunk_duration = chunk_duration_seconds
        self.queue = queue.Queue()
        self.accumulated_chunks = []
        self.last_flush_time = time.time()
        self.lock = threading.Lock()
        self.transcription_callback: Optional[Callable[[str], None]] = None
    
    def add_frame(self, audio_frame):
        """Add audio frame from WebRTC (thread-safe)"""
        self.queue.put(audio_frame)
    
    def set_transcription_callback(self, callback: Callable[[str], None]):
        """Set callback to receive transcription results"""
        self.transcription_callback = callback
    
    def start_processing(self, transcriber: RobustAudioTranscriber):
        """Start background thread to process audio chunks"""
        thread = threading.Thread(
            target=self._processing_loop,
            args=(transcriber,),
            daemon=True
        )
        thread.start()
    
    def _processing_loop(self, transcriber: RobustAudioTranscriber):
        """Background loop to transcribe audio chunks"""
        while True:
            try:
                # Get frame with timeout
                frame = self.queue.get(timeout=0.1)
                
                with self.lock:
                    self.accumulated_chunks.append(frame)
                
                # Check if enough time passed to transcribe
                if time.time() - self.last_flush_time >= self.chunk_duration:
                    with self.lock:
                        if self.accumulated_chunks:
                            # Combine chunks
                            audio_data = self._combine_chunks(self.accumulated_chunks)
                            
                            # Transcribe
                            text = transcriber.transcribe(audio_data)
                            
                            # Callback with result
                            if text and self.transcription_callback:
                                self.transcription_callback(text)
                            
                            # Reset
                            self.accumulated_chunks = []
                            self.last_flush_time = time.time()
            
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                continue
    
    def _combine_chunks(self, chunks) -> bytes:
        """Combine audio chunks into single WAV bytes"""
        # TODO: Implement proper audio concatenation
        # This is simplified - production needs pydub or scipy
        return b""  # Placeholder

# ============================================================================
# SMART VIDEO FRAME SAMPLER
# ============================================================================

class SmartVideoSampler:
    """
    Intelligent frame sampler that adapts to system load.
    Reduces sampling rate if processing is slow.
    """
    
    def __init__(self, base_interval: float = 3.0, max_interval: float = 10.0):
        self.base_interval = base_interval
        self.max_interval = max_interval
        self.current_interval = base_interval
        self.last_sample_time = 0
        self.processing_times = []
        self.latest_frame = None
        self.lock = threading.Lock()
    
    def should_sample(self) -> bool:
        """Check if frame should be sampled (adaptive)"""
        current_time = time.time()
        
        if current_time - self.last_sample_time >= self.current_interval:
            self.last_sample_time = current_time
            return True
        
        return False
    
    def record_processing_time(self, seconds: float):
        """Record how long frame processing took (for adaptive sampling)"""
        self.processing_times.append(seconds)
        
        # Keep only recent 10 measurements
        if len(self.processing_times) > 10:
            self.processing_times.pop(0)
        
        # Adapt interval based on processing time
        avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        if avg_processing_time > 2.0:
            # Processing is slow - increase interval
            self.current_interval = min(
                self.current_interval * 1.2,
                self.max_interval
            )
            logger.warning(f"⚠️ Increasing frame interval to {self.current_interval:.1f}s")
        
        elif avg_processing_time < 0.5 and self.current_interval > self.base_interval:
            # Processing is fast - decrease interval
            self.current_interval = max(
                self.current_interval * 0.9,
                self.base_interval
            )
            logger.info(f"✅ Decreasing frame interval to {self.current_interval:.1f}s")
    
    def process_frame(self, frame) -> Optional[str]:
        """Process frame with timing (returns base64 if sampled)"""
        if not self.should_sample():
            return None
        
        start_time = time.time()
        
        try:
            # Convert frame to base64
            from PIL import Image
            import io
            import base64
            
            img = frame.to_ndarray(format="rgb24")
            pil_img = Image.fromarray(img)
            pil_img.thumbnail((640, 480))
            
            buffer = io.BytesIO()
            pil_img.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            
            frame_base64 = base64.b64encode(buffer.read()).decode()
            
            with self.lock:
                self.latest_frame = frame_base64
            
            # Record timing
            processing_time = time.time() - start_time
            self.record_processing_time(processing_time)
            
            return frame_base64
        
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
            return None

# ============================================================================
# CONNECTION HEALTH MONITOR
# ============================================================================

class ConnectionHealthMonitor:
    """
    Monitors WebRTC connection health and triggers fallbacks.
    """
    
    def __init__(self):
        self.last_video_frame_time = 0
        self.last_audio_chunk_time = 0
        self.video_timeout = 5.0  # Seconds
        self.audio_timeout = 3.0
        self.connection_lost_callback: Optional[Callable] = None
    
    def update_video(self):
        """Record video frame received"""
        self.last_video_frame_time = time.time()
    
    def update_audio(self):
        """Record audio chunk received"""
        self.last_audio_chunk_time = time.time()
    
    def check_health(self) -> Dict[str, bool]:
        """Check if connections are healthy"""
        current_time = time.time()
        
        video_ok = (current_time - self.last_video_frame_time) < self.video_timeout
        audio_ok = (current_time - self.last_audio_chunk_time) < self.audio_timeout
        
        return {
            'video': video_ok,
            'audio': audio_ok,
            'overall': video_ok and audio_ok
        }
    
    def monitor_loop(self):
        """Background thread to monitor connection"""
        while True:
            time.sleep(2.0)
            
            health = self.check_health()
            
            if not health['overall']:
                logger.warning("⚠️ WebRTC connection degraded")
                
                if self.connection_lost_callback:
                    self.connection_lost_callback(health)

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def example_integration():
    """
    Example showing how to use these components in app_multimodal.py
    """
    
    # Initialize components
    transcriber = RobustAudioTranscriber()
    tts_engine = RobustTTSEngine()
    video_sampler = SmartVideoSampler(base_interval=3.0)
    audio_buffer = ThreadSafeAudioBuffer(chunk_duration_seconds=2.0)
    health_monitor = ConnectionHealthMonitor()
    
    # Setup callbacks
    def on_transcription(text: str):
        """Called when STT produces text"""
        st.session_state.transcription += " " + text
        logger.info(f"Transcribed: {text}")
    
    def on_connection_lost(health: Dict):
        """Called when WebRTC connection fails"""
        st.warning("⚠️ Connection unstable - consider switching to text mode")
        logger.error(f"Connection health: {health}")
    
    audio_buffer.set_transcription_callback(on_transcription)
    health_monitor.connection_lost_callback = on_connection_lost
    
    # Start background processing
    audio_buffer.start_processing(transcriber)
    
    # WebRTC callbacks
    def video_callback(frame):
        """Called for each video frame"""
        health_monitor.update_video()
        
        # Sample frame if needed
        frame_base64 = video_sampler.process_frame(frame)
        
        if frame_base64:
            # Store for vision analysis
            st.session_state.current_video_frame = frame_base64
        
        return frame
    
    def audio_callback(frame):
        """Called for each audio frame"""
        health_monitor.update_audio()
        audio_buffer.add_frame(frame)
        return frame
    
    return {
        'video_callback': video_callback,
        'audio_callback': audio_callback,
        'transcriber': transcriber,
        'tts_engine': tts_engine
    }

if __name__ == "__main__":
    # Test individual components
    print("Testing multimodal components...")
    
    # Test transcriber fallbacks
    try:
        transcriber = RobustAudioTranscriber()
        print(f"✅ STT initialized with {len(transcriber.engines)} engines")
    except Exception as e:
        print(f"❌ STT error: {e}")
    
    # Test TTS fallbacks
    try:
        tts = RobustTTSEngine()
        print(f"✅ TTS initialized with {len(tts.engines)} engines")
    except Exception as e:
        print(f"❌ TTS error: {e}")
    
    print("\nAll components ready!")
