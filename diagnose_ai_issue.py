#!/usr/bin/env python
"""
Diagnose why AI feedback isn't working
"""
import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, r'c:\Users\user\OneDrive\Desktop\CareerFlow AI')
django.setup()

from interviews.services.ollama_engine import ollama_engine
import requests

print("=" * 80)
print("DIAGNOSING AI INTEGRATION ISSUE")
print("=" * 80)

# Step 1: Health check
print("\n[STEP 1] Testing Ollama health check...")
try:
    is_avail = ollama_engine.is_available()
    print(f"  ✓ is_available() returned: {is_avail}")
    if not is_avail:
        print(f"  ✗ PROBLEM: is_available() is False")
        print(f"    This will cause fallback to 5/10 with no feedback")
except Exception as e:
    print(f"  ✗ Exception: {e}")

# Step 2: Direct endpoint test
print("\n[STEP 2] Testing /api/tags endpoint directly...")
try:
    resp = requests.get(f"{ollama_engine.host}/api/tags", timeout=5)
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        models = data.get('models', [])
        print(f"  Models: {len(models)} available")
        for m in models:
            print(f"    - {m.get('name')}")
    else:
        print(f"  ✗ Unexpected status code: {resp.status_code}")
except Exception as e:
    print(f"  ✗ Exception: {e}")

# Step 3: Test _send_prompt method
print("\n[STEP 3] Testing _send_prompt (will call Ollama)...")
print("  Sending simple test prompt...")
try:
    response_text = ollama_engine._send_prompt(
        "Respond with ONLY: {\"test\": \"ok\"}",
        timeout=15
    )
    print(f"  Response (first 150 chars): {response_text[:150]}")
    
    # Check if it looks like JSON
    if '{' in response_text and '}' in response_text:
        print(f"  ✓ Response contains JSON-like structure")
    else:
        print(f"  ✗ Response doesn't contain JSON")
except Exception as e:
    print(f"  ✗ Exception: {e}")

# Step 4: Test evaluate_answer
print("\n[STEP 4] Testing evaluate_answer...")
try:
    evaluation = ollama_engine.evaluate_answer(
        question="Describe your Python experience",
        answer="I have 5+ years with Django and REST APIs",
        role="Python Developer"
    )
    print(f"  Score: {evaluation.get('score', 'MISSING')}")
    print(f"  Feedback: {evaluation.get('feedback', 'MISSING')[:100]}...")
    print(f"  Topics: {evaluation.get('topics_to_cover', 'MISSING')[:100]}...")
    
    if evaluation.get('feedback') == 'No feedback available':
        print(f"\n  ⚠ ISSUE: Got default 'No feedback available'")
        print(f"    This means evaluate_answer couldn't parse Ollama's response")
    else:
        print(f"\n  ✓ Got actual AI feedback!")
except Exception as e:
    print(f"  ✗ Exception: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
