# 🚀 Streamlit Cloud Deployment Guide

## The Problem
Streamlit Cloud **does not support `.env` files** for security reasons. Instead, it uses **`secrets.toml`** format.

## ✅ Solution (Already Implemented)

The app now automatically detects the environment:
- **Streamlit Cloud**: Uses `st.secrets` (secrets.toml format)
- **Local Development**: Uses `.env` file

No code changes needed on your part!

---

## 📋 How to Deploy on Streamlit Cloud

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Add Streamlit Cloud secrets support"
git push origin main
```

**Important**: Make sure `.env` is in `.gitignore` (already done ✅)

### Step 2: Configure Secrets on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Deploy your app from GitHub repo: `Aryan10022006/ai-interviewer-coach`
3. Once deployed, click **"⚙️ Settings"** → **"Secrets"**
4. Paste this content (with your actual keys):

```toml
# Streamlit Cloud Secrets
GOOGLE_API_KEY = "AIzaSyD4a6WDAY_Q9G0ljwIesix1Vd8OzYTKz94"
GROQ_API_KEY = "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"
TAVILY_API_KEY = "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"
```

5. Click **"Save"**
6. Your app will automatically restart with the new secrets

---

## 🔄 How It Works

### Local Development (`.env` file)
```python
# agents.py tries Streamlit secrets first
try:
    google_api_key = st.secrets["GOOGLE_API_KEY"]  # Fails locally
except:
    load_dotenv()  # Falls back to .env ✅
    google_api_key = os.getenv("GOOGLE_API_KEY")
```

### Streamlit Cloud (`secrets.toml`)
```python
# agents.py tries Streamlit secrets first
try:
    google_api_key = st.secrets["GOOGLE_API_KEY"]  # Success! ✅
except:
    # Never reaches this on cloud
```

---

## 📝 Secrets Format Comparison

| **Local (.env)** | **Streamlit Cloud (secrets.toml)** |
|------------------|-----------------------------------|
| `GOOGLE_API_KEY=abc123` | `GOOGLE_API_KEY = "abc123"` |
| No quotes needed | Quotes **required** |
| Loaded via `python-dotenv` | Loaded via `st.secrets` |

---

## ⚠️ Common Deployment Errors

### Error: "No LLM configured!"
**Cause**: Secrets not set or wrong format

**Fix**:
1. Go to app Settings → Secrets
2. Make sure keys are in quotes: `GOOGLE_API_KEY = "your_key"`
3. Check for typos in key names (case-sensitive!)

### Error: "streamlit.errors.StreamlitAPIException"
**Cause**: Using `st.secrets` in local development without `.streamlit/secrets.toml`

**Fix**: Already handled! App falls back to `.env` automatically ✅

---

## 🎯 Test Your Deployment

After deploying, check the logs:
- ✅ **Success**: `🔐 Using Streamlit Cloud secrets`
- ✅ **Success**: `🔑 Google API Key: ✅ Found`
- ❌ **Error**: `❌ No LLM configured!` → Fix secrets format

---

## 📦 Which Files to Deploy?

**Include** (already in repo):
- ✅ `app.py`, `app_multimodal.py`
- ✅ `agents.py` (now supports both .env and secrets)
- ✅ `requirements.txt`
- ✅ `.streamlit/secrets.toml.example` (template only)

**Exclude** (never commit):
- ❌ `.env` (in .gitignore)
- ❌ `.streamlit/secrets.toml` (in .gitignore)

---

## 🔒 Security Best Practices

1. **Never commit API keys to GitHub**
   - ✅ `.env` is in `.gitignore`
   - ✅ `.streamlit/` is in `.gitignore`

2. **Rotate keys if accidentally committed**
   - Regenerate keys immediately
   - Update secrets on Streamlit Cloud

3. **Use different keys for dev/prod**
   - Local: Development keys in `.env`
   - Cloud: Production keys in secrets.toml

---

## 🎉 You're Done!

Your app now works seamlessly on:
- 💻 **Local**: Uses `.env` file
- ☁️ **Streamlit Cloud**: Uses secrets.toml (set via UI)

No code duplication, no manual switching! 🚀
