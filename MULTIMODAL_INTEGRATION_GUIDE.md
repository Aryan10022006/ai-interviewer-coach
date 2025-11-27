# 🎥 Multimodal Audio/Video Interview System - Integration Guide

## 📋 Overview

This upgrade adds **real-time audio/video capabilities** to your interview simulator while keeping the LangGraph state machine **completely unchanged**.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE LAYER (NEW)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   WebRTC     │  │  STT Engine  │  │  TTS Engine  │     │
│  │  (Video/Mic) │  │  (Whisper/   │  │  (gTTS/      │     │
│  │              │  │   Google)    │  │   OpenAI)    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                  ┌─────────▼─────────┐                      │
│                  │  Interface Bridge │                      │
│                  │  (Text Adapter)   │                      │
│                  └─────────┬─────────┘                      │
└────────────────────────────┼──────────────────────────────┘
                             │
┌────────────────────────────▼──────────────────────────────┐
│                    BRAIN LAYER (UNCHANGED)                 │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Profiler │→ │Researcher│→ │Interviewer│→ │  Critic  │ │
│  │  Agent   │  │  Agent   │  │  Agent    │  │  Agent   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
│                                                             │
│              LangGraph State Machine                       │
│              (agents.py, graph.py, state.py)              │
└────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Design Principles

### 1. **Brain is Untouched**
- `agents.py` - NO CHANGES
- `graph.py` - NO CHANGES
- `state.py` - NO CHANGES
- `db_manager.py` - NO CHANGES

The interviewer agents don't know if input came from keyboard or microphone. They just process text.

### 2. **Interface Layer Only**
All multimodal logic lives in `app_multimodal.py`:
- WebRTC streaming
- Audio transcription (STT)
- Speech synthesis (TTS)
- Video frame sampling
- Confidence scoring

### 3. **Graceful Fallback**
If WebRTC fails or APIs unavailable, system falls back to text mode automatically.

---

## 🔧 Installation

### Step 1: Install Dependencies

```bash
# Install multimodal packages
pip install -r requirements_multimodal.txt

# Or manually:
pip install streamlit-webrtc av pydub gTTS SpeechRecognition scipy soundfile
```

**Windows users:** PyAudio might need manual installation:
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux users:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

### Step 2: Configure API Keys (Optional)

For premium features, add to `.env`:

```bash
# OpenAI (for Whisper STT + Premium TTS)
OPENAI_API_KEY=sk-...your_key_here

# ElevenLabs (for ultra-realistic TTS - optional)
ELEVENLABS_API_KEY=...your_key_here
```

**Free alternatives (no API key needed):**
- STT: Google Speech Recognition (built-in)
- TTS: gTTS (Google Text-to-Speech)

### Step 3: Run Multimodal App

```bash
streamlit run app_multimodal.py
```

---

## 🎥 Feature Breakdown

### 1. Video Pipeline: "Non-Verbal Coach"

**Technology:** `streamlit-webrtc` + Gemini Flash Vision

**Flow:**
```python
Webcam → WebRTC → Frame Sampling (every 3s) → Base64 Encode
    → VisionCoachAgent (existing!) → Confidence Score (1-10)
    → Update State → Display in UI
```

**Implementation:**
```python
class VideoFrameSampler:
    def __init__(self, sample_interval_seconds=3.0):
        self.sample_interval = sample_interval_seconds
        self.last_sample_time = 0
    
    def process_frame(self, frame: av.VideoFrame) -> Optional[str]:
        """Sample frame every N seconds to avoid latency"""
        if not self.should_sample_frame():
            return None
        
        # Convert to PIL, resize, encode to base64
        img = frame.to_ndarray(format="rgb24")
        pil_img = Image.fromarray(img)
        pil_img.thumbnail((640, 480))
        
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.read()).decode()
```

**Why Frame Sampling?**
- Processing every frame (30 FPS) = too slow
- Sample 1 frame every 3 seconds = smooth UX
- Gemini Flash analyzes frame in ~500ms

**Confidence Scoring:**
Uses your existing `VisionCoachAgent` from `agents.py`:
```python
from agents import VisionCoachAgent

vision_coach = VisionCoachAgent()
result = vision_coach.analyze({
    'current_video_frame': frame_base64,
    'current_question': question,
    'current_answer': answer
})

confidence_score = result['confidence_score']  # 1-10
```

---

### 2. Audio Input Pipeline: STT (Speech-to-Text)

**Technology:** OpenAI Whisper (premium) or Google Speech (free)

**Flow:**
```python
Microphone → WebRTC Audio Stream → Audio Chunks (2s)
    → Whisper/Google API → Transcribed Text
    → Feed to graph.process_user_answer() (UNCHANGED)
```

**Implementation:**
```python
class AudioTranscriber:
    def __init__(self, method="google"):  # "whisper" or "google"
        self.method = method
        self.recognizer = sr.Recognizer()
    
    def transcribe_audio_chunk(self, audio_data: bytes) -> str:
        """Convert speech to text"""
        if self.method == "whisper":
            # OpenAI Whisper (more accurate, requires API key)
            response = openai.Audio.transcribe("whisper-1", audio_file)
            return response["text"]
        
        elif self.method == "google":
            # Google Speech (free, less accurate)
            audio = sr.AudioData(audio_data, sample_rate=16000, sample_width=2)
            return self.recognizer.recognize_google(audio)
```

**Why Audio Chunks?**
- Real-time transcription needs buffering
- Process every 2 seconds of audio
- Display live transcription in UI
- User clicks "Submit" when done

**Accuracy Comparison:**

| Engine | Accuracy | Speed | Cost |
|--------|----------|-------|------|
| OpenAI Whisper | 95%+ | ~1s per 10s audio | $0.006/min |
| Google Speech | 85-90% | Real-time | FREE |

---

### 3. Audio Output Pipeline: TTS (Text-to-Speech)

**Technology:** gTTS (free) or OpenAI TTS (premium)

**Flow:**
```python
Interviewer generates question (text)
    → TTS Engine → Audio MP3 bytes
    → st.audio(autoplay=True) → AI speaks question
```

**Implementation:**
```python
class AudioSynthesizer:
    def __init__(self, method="gtts"):  # "gtts" or "openai"
        self.method = method
    
    def synthesize_text(self, text: str) -> bytes:
        """Convert text to speech"""
        if self.method == "gtts":
            # Google TTS (free, robotic)
            tts = gTTS(text=text, lang='en', slow=False)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            return buffer.read()
        
        elif self.method == "openai":
            # OpenAI TTS (premium, natural)
            response = openai.Audio.speech.create(
                model="tts-1",
                voice="alloy",  # or nova, shimmer, fable, onyx, echo
                input=text
            )
            return response.content
```

**Auto-Play Feature:**
```python
def play_audio(text: str):
    """Automatically play interviewer's question"""
    audio_bytes = synthesizer.synthesize_text(text)
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
```

**Voice Quality:**

| Engine | Naturalness | Speed | Cost |
|--------|-------------|-------|------|
| gTTS | 5/10 (robotic) | ~1s | FREE |
| OpenAI TTS | 9/10 (natural) | ~1s | $15/1M chars |
| ElevenLabs | 10/10 (ultra-realistic) | ~2s | $5/month |

---

## 🔄 Integration with Existing LangGraph

### The Bridge: `process_multimodal_answer()`

This function is the **interface adapter** that bridges WebRTC → LangGraph:

```python
def process_multimodal_answer(transcribed_text: str):
    """
    Interface layer that converts multimodal input to text for LangGraph.
    The brain doesn't know if input came from mic or keyboard.
    """
    
    # 1. Add video frame to state (if available)
    if st.session_state.current_video_frame:
        st.session_state.state['current_video_frame'] = st.session_state.current_video_frame
        st.session_state.state['video_enabled'] = True
    
    # 2. Add confidence score from vision analysis
    st.session_state.state['confidence_score'] = st.session_state.confidence_score
    
    # 3. Call UNCHANGED brain - it just sees text
    result = process_user_answer(
        st.session_state.state,  # Current state
        transcribed_text         # User's answer (from mic or keyboard)
    )
    
    # 4. Update state
    st.session_state.state = result
    
    # 5. Get next question
    next_question = result.get('current_question', '')
    
    # 6. Convert question to speech (TTS)
    if next_question and st.session_state.tts_enabled:
        synthesizer = AudioSynthesizer(method="gtts")
        play_audio(next_question, synthesizer)
    
    # 7. Update chat history
    st.session_state.messages.append({
        'role': 'user',
        'content': transcribed_text
    })
    st.session_state.messages.append({
        'role': 'assistant',
        'content': next_question
    })
```

### Key Point: Brain Sees Only Text

```python
# Text mode input
user_types_answer = "I used Redis for caching"
process_user_answer(state, user_types_answer)  # ✅

# Audio mode input (transcribed)
user_speaks_answer = "I used Redis for caching"  # From STT
process_user_answer(state, user_speaks_answer)  # ✅ Same!

# Brain doesn't know the difference! 🧠
```

---

## 🎛️ UI/UX Flow

### Mode Toggle (Sidebar)

```python
st.sidebar.radio(
    "Interview Mode:",
    options=['text', 'av'],
    format_func=lambda x: "⌨️ Text Mode" if x == 'text' else "🎥 Live A/V Mode"
)
```

### Text Mode (Original)

```
┌─────────────────────────────────────┐
│ 🎤 Interviewer:                     │
│ "Explain your system design work"   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Your Answer:                        │
│ [Text area - type here]             │
│                                     │
└─────────────────────────────────────┘

[Submit Answer]
```

### A/V Mode (New)

```
┌───────────────────┐  ┌──────────────────┐
│                   │  │ 🎯 Real-Time     │
│   📹 Your Video   │  │    Feedback      │
│                   │  │                  │
│   [WebRTC Feed]   │  │ Confidence: 7/10 │
│                   │  │ ⭐⭐⭐⭐⭐⭐⭐ │
│   🔴 Recording... │  │                  │
│                   │  │ 🎤 Transcription:│
│                   │  │ "I used Redis    │
│                   │  │  for caching..." │
└───────────────────┘  │                  │
                       │ [✅ Submit]      │
                       └──────────────────┘

🔊 [Audio player - AI speaks question]
```

---

## ⚡ Performance Optimizations

### 1. Frame Sampling Strategy

**Problem:** Processing 30 FPS = 30 API calls/sec = slow + expensive

**Solution:** Sample 1 frame every 3 seconds

```python
sample_interval_seconds = 3.0  # Adjustable in UI

def should_sample_frame(self):
    """Only sample if interval passed"""
    current_time = time.time()
    if current_time - self.last_sample_time >= self.sample_interval:
        self.last_sample_time = current_time
        return True
    return False
```

**Impact:**
- 30 FPS → 0.33 FPS sampling
- 99% reduction in processing
- Still captures body language changes

### 2. Audio Chunking

**Problem:** Real-time STT needs audio buffering

**Solution:** Process audio in 2-second chunks

```python
chunk_duration = 2.0  # Process every 2 seconds

def process_audio_queue():
    audio_chunks = []
    
    while True:
        frame = audio_queue.get()
        audio_chunks.append(frame)
        
        if time.time() - last_process_time >= chunk_duration:
            combined = combine_audio_frames(audio_chunks)
            text = transcriber.transcribe_audio_chunk(combined)
            
            # Update live transcription
            st.session_state.transcription += " " + text
            
            audio_chunks = []
```

**Benefits:**
- Smooth real-time display
- Reduced API calls
- User sees live transcription

### 3. Async Processing

```python
webrtc_streamer(
    # ...
    async_processing=True  # ← Process frames in background thread
)
```

This prevents UI blocking during:
- Video frame encoding
- Vision analysis API calls
- Audio transcription

---

## 🧪 Testing Checklist

### Basic Functionality

- [ ] **Text Mode**: Original interview works (no regression)
- [ ] **A/V Mode Toggle**: Switch between modes in sidebar
- [ ] **Webcam Access**: WebRTC connects, video displays
- [ ] **Microphone Access**: Audio stream working
- [ ] **Frame Sampling**: Captures 1 frame every 3s
- [ ] **Live Transcription**: Updates in real-time
- [ ] **Submit Answer**: Transcribed text processes correctly
- [ ] **TTS Playback**: AI question plays as audio
- [ ] **Confidence Score**: Updates from video analysis

### Integration Testing

- [ ] **LangGraph Unchanged**: Brain receives same text format
- [ ] **Critic Scoring**: Works with transcribed answers
- [ ] **Pushback System**: Triggers correctly (score ≤2)
- [ ] **Early Termination**: Works with A/V mode
- [ ] **Database Logging**: Saves A/V sessions correctly
- [ ] **Video Frame Storage**: Frames saved to state
- [ ] **Session Viewer**: Can review A/V sessions

### Error Handling

- [ ] **No Webcam**: Falls back to text mode gracefully
- [ ] **No Mic**: Shows warning, allows text input
- [ ] **STT Failure**: Shows error, doesn't crash
- [ ] **TTS Failure**: Displays text as fallback
- [ ] **API Timeout**: Handles gracefully
- [ ] **Network Loss**: Saves progress, allows resume

### Performance

- [ ] **Frame Rate**: Smooth video display (no lag)
- [ ] **Transcription Latency**: <2s delay
- [ ] **TTS Generation**: <1s for typical question
- [ ] **CPU Usage**: <50% during A/V session
- [ ] **Memory Usage**: <1GB RAM

---

## 🐛 Troubleshooting

### "WebRTC connection failed"

**Problem:** Browser can't access camera/mic

**Solutions:**
1. Allow camera/mic permissions in browser
2. Use HTTPS (WebRTC requires secure context)
3. Check firewall settings
4. Try different browser (Chrome/Firefox recommended)

**Temporary Fix:**
```python
# Add to sidebar
if webrtc_ctx.state.playing:
    st.success("✅ Connected")
else:
    st.error("❌ WebRTC failed - switch to Text Mode")
```

### "Transcription is empty"

**Problem:** STT not recognizing speech

**Solutions:**
1. Speak louder/clearer
2. Reduce background noise
3. Switch from Google to Whisper (more accurate)
4. Check microphone settings in OS

**Debug:**
```python
# Add to audio processor
print(f"Audio level: {np.abs(audio_data).mean()}")  # Should be >0.01
```

### "TTS not playing"

**Problem:** Audio autoplay blocked by browser

**Solutions:**
1. Click "Allow autoplay" in browser
2. User interaction required first (click button)
3. Use `st.audio()` without autoplay

**Fallback:**
```python
try:
    st.audio(audio_bytes, autoplay=True)
except:
    st.audio(audio_bytes)  # Manual play button
    st.info("Click play button to hear question")
```

### "High CPU usage"

**Problem:** Too many frames being processed

**Solutions:**
1. Increase frame sample interval (3s → 5s)
2. Reduce video resolution (640x480 → 320x240)
3. Use `async_processing=True`

**Optimization:**
```python
# Reduce resolution in WebRTC config
media_stream_constraints={
    "video": {
        "width": 320,   # Lower
        "height": 240,  # Lower
        "frameRate": 15  # Cap FPS
    }
}
```

---

## 🚀 Advanced Features (Future)

### 1. Multi-Language Support

```python
# Detect language from audio
from langdetect import detect

language = detect(transcribed_text)  # 'en', 'es', 'fr', etc.

# Use appropriate TTS voice
tts = gTTS(text=text, lang=language)
```

### 2. Emotion Detection

```python
# Analyze facial emotions (happy, nervous, confident)
from deepface import DeepFace

emotion = DeepFace.analyze(frame, actions=['emotion'])
state['emotion'] = emotion['dominant_emotion']
```

### 3. Filler Word Detection

```python
# Count "um", "uh", "like"
filler_words = ['um', 'uh', 'like', 'you know', 'sort of']
count = sum(transcribed_text.lower().count(word) for word in filler_words)

st.metric("Filler Words", count)
if count > 5:
    st.warning("⚠️ Try to reduce filler words")
```

### 4. Pace Analysis

```python
# Words per minute
words = len(transcribed_text.split())
duration = audio_duration_seconds
wpm = (words / duration) * 60

if wpm < 100:
    st.info("Speaking too slowly")
elif wpm > 160:
    st.warning("Speaking too fast")
else:
    st.success(f"Good pace: {wpm:.0f} WPM")
```

---

## 📊 Comparison: Text vs A/V Mode

| Feature | Text Mode | A/V Mode |
|---------|-----------|----------|
| **Input** | Keyboard typing | Voice + Video |
| **Output** | Text display | Audio playback |
| **Feedback** | Text only | Verbal + Non-verbal |
| **Latency** | Instant | 1-2s (STT delay) |
| **Accuracy** | 100% | 85-95% (STT) |
| **Realism** | Low | High (real interview) |
| **CPU Usage** | Low | Medium-High |
| **API Calls** | Same (brain) | +STT +TTS +Vision |
| **Cost** | Free | Free (Google) or Paid (OpenAI) |
| **Setup** | None | Camera/Mic required |

---

## 🎯 Summary

### What You Get

✅ **Real-time video analysis** (body language, confidence)  
✅ **Speech-to-text** (speak answers instead of typing)  
✅ **Text-to-speech** (AI speaks questions)  
✅ **Live transcription** (see what you're saying in real-time)  
✅ **Mode toggle** (switch between text/A/V anytime)  
✅ **Zero brain changes** (LangGraph untouched)  
✅ **Graceful fallbacks** (works without APIs)  
✅ **Performance optimized** (frame sampling, chunking)

### Architecture

```
Interface Layer (NEW)        Brain Layer (UNCHANGED)
─────────────────────        ───────────────────────
WebRTC → STT → Text   ────→  process_user_answer()
                                    ↓
Video → Vision → Score ───→  CriticAgent.evaluate()
                                    ↓
Text → TTS → Audio    ←────  InterviewerAgent.ask()
```

### Quick Start

```bash
# Install
pip install -r requirements_multimodal.txt

# Run
streamlit run app_multimodal.py

# Toggle mode in sidebar: Text ⌨️ or A/V 🎥
```

---

**Next Steps:**
1. Test basic WebRTC connection
2. Configure STT/TTS engines
3. Integrate with existing VisionCoachAgent
4. Add error handling
5. Deploy with HTTPS (required for WebRTC)
