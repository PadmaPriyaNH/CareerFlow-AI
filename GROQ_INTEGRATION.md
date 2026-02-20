# CareerFlow AI - Groq Integration Guide

## 🎯 What Just Changed

I've implemented a **provider-agnostic AI service** that works with both **Groq** (cloud, fast) and **Ollama** (local, free CPU).

### Key Improvements:
- ⚡ **Response time**: 1-3 seconds (Groq) vs 50-90+ seconds (Ollama CPU)
- 🌐 **Internet**: Groq requires internet, Ollama works offline
- 💰 **Cost**: Groq free tier covers personal use, Ollama is completely free
- 🔄 **Flexibility**: Switch providers by changing one environment variable

---

## 🚀 Quick Setup

### Option 1: Use Groq (Recommended - Fastest)

**Step 1: Get a Groq API Key**
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Go to "API Keys" and create a new key
4. Save the key (starts with `gsk_`)

**Step 2: Update Your .env File**
```
# Copy .env.example to .env and set these:
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=mistral-7b-instruct-v0.2
```

**Step 3: Test It**
```powershell
.\.venv\Scripts\activate
python test_ai_service.py
```

Expected output: All tests pass with Groq ✓

---

### Option 2: Keep Using Ollama (Local, No API Key)

**Step 1: Make Sure Ollama is Running**
```powershell
# Terminal 1: Start Ollama
ollama serve
```

**Step 2: Update Your .env File**
```
# Use Ollama instead of Groq
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
```

**Step 3: Test It**
```powershell
.\.venv\Scripts\activate
python test_ai_service.py
```

---

## 📋 File Changes Summary

### New Files Created:
- **`interviews/services/ai_service.py`** - Provider-agnostic AI service supporting Groq & Ollama

### Modified Files:
- **`requirements.txt`** - Added `langchain-groq` and `langchain-ollama`
- **`.env.example`** - Updated with Groq configuration
- **`interviews/models.py`** - Updated to use `ai_service` instead of `ollama_engine`
- **`interviews/views.py`** - Updated to use `ai_service` instead of `ollama_engine`

---

## 🔧 How It Works

### The AIService Class

```python
from interviews.services.ai_service import ai_service

# Automatically picks Groq or Ollama based on AI_PROVIDER env var
# Parse resume
data = ai_service.parse_resume(resume_text)

# Evaluate answer
feedback = ai_service.evaluate_answer(question, answer, role)

# Generate questions
questions = ai_service.generate_questions(job_desc, role, skills)

# Check availability
if ai_service.is_available():
    # Get AI feedback
else:
    # Use fallback
```

### Switching Providers is Simple

```env
# For Groq (fast, cloud):
AI_PROVIDER=groq
GROQ_API_KEY=gsk_your_key

# For Ollama (local, offline):
AI_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
```

---

## 📊 Performance Comparison

| Feature | Groq | Ollama (CPU) |
|---------|------|--------------|
| Response Time | 1-3 seconds ⚡ | 50-90+ seconds 🐌 |
| API Key Required | Yes | No |
| Offline Support | No | Yes ✓ |
| Free Tier | Yes (10-30 RPM) | Yes (unlimited) |
| Cost at Scale | Pay per token | Your hardware |
| Setup Difficulty | 2 minutes | 10+ minutes |

---

## ✅ Testing

### Run the Test Suite

```powershell
.\.venv\Scripts\activate
python test_ai_service.py
```

This will:
1. Check which provider is active
2. Test resume parsing
3. Test answer evaluation
4. Test question generation

Expected output (with Groq):
```
[TEST 1] AI Provider: GROQ
[TEST 1] Status: ✓ AVAILABLE
[TEST 2] Testing Resume Parsing... ✓
[TEST 3] Testing Answer Evaluation... ✓
[TEST 4] Testing Question Generation... ✓

ALL TESTS COMPLETED SUCCESSFULLY! ✓
```

---

## 🚀 Start Using It

### 1. Update Your .env
```bash
cp .env.example .env
# Edit .env and set:
# - AI_PROVIDER=groq
# - GROQ_API_KEY=gsk_your_key
```

### 2. Run Migrations (if needed)
```powershell
.\.venv\Scripts\activate
python manage.py migrate
```

### 3. Start Django
```powershell
.\.venv\Scripts\activate
python manage.py runserver
```

### 4. Test an Interview
- Visit http://localhost:8000
- Create account
- Upload resume
- Start interview
- **You should get AI feedback in 1-3 seconds!** ⚡

---

## 🐛 Troubleshooting

### "GROQ_API_KEY not set" Error
**Solution**: Set `GROQ_API_KEY` in your .env file
```
GROQ_API_KEY=gsk_your_actual_key_here
```

### "Ollama is not responding" Error
**Solution**: Make sure Ollama is running
```powershell
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Test it
curl http://localhost:11434/api/tags
```

### "AI service is unavailable" Message in Interview
**Causes**:
- Groq: API key is invalid or expired
- Ollama: Service isn't running
- Network: No internet connection (for Groq)

**Solution**: Check your .env file and make sure the service is running

---

## 📚 Advanced: Using Different Groq Models

Groq supports multiple models with different speeds/capabilities:

```env
# Faster, more direct:
GROQ_MODEL=llama3-8b-8192

# Balanced:
GROQ_MODEL=mistral-7b-instruct-v0.2

# Better quality (slower):
GROQ_MODEL=llama-2-70b-chat
```

All are free on Groq's free tier with rate limits.

---

## 🔐 Security Notes

1. **Never commit `.env`** - It contains your API key
2. **Use environment variables** in production (Azure App Settings, GitHub Secrets, etc.)
3. **Rotate API keys** periodically
4. **Monitor usage** in Groq console to avoid unexpected charges

---

## 📖 Next Steps

1. ✅ Complete the setup above
2. ✅ Run `python test_ai_service.py`
3. ✅ Start Django and test an interview
4. ✅ (Optional) Deploy to Azure using Groq

---

## 💡 Tips

- **Local Development**: Use Groq for speed, or Ollama if you don't have internet
- **Production**: Use Groq (it's more reliable than running Ollama on consumer hardware)
- **Backup**: Keep Ollama as a fallback if Groq API fails
- **Testing**: The AIService has built-in fallback to default questions if evaluation fails

---

## Questions?

If something doesn't work:
1. Check your .env file is correctly set up
2. Run `python test_ai_service.py` to diagnose
3. Check provider status: `python -c "from interviews.services.ai_service import ai_service; print(f'Provider: {ai_service.provider}')"` 
4. Review the logs in Django for detailed error messages

Good luck! 🚀
