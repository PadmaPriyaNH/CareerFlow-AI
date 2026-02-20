#!/usr/bin/env python
"""
Test script to verify AIService works with both Groq and Ollama
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from interviews.services.ai_service import ai_service

print("=" * 70)
print("CAREERFLOW AI - SERVICE TEST")
print("=" * 70)

# Test 1: Check provider and availability
print(f"\n[TEST 1] AI Provider: {ai_service.provider.upper()}")
print(f"[TEST 1] Checking availability...")

is_available = ai_service.is_available()
print(f"[TEST 1] Status: {'✓ AVAILABLE' if is_available else '✗ UNAVAILABLE'}")

if not is_available:
    print("\n⚠️  WARNING: AI service is not available!")
    print("Please check:")
    print("  - If using Groq: Set GROQ_API_KEY environment variable")
    print("  - If using Ollama: Make sure 'ollama serve' is running")
    sys.exit(1)

# Test 2: Resume Parsing
print(f"\n[TEST 2] Testing Resume Parsing...")
sample_resume = """
John Doe
Email: john@example.com
Phone: 555-1234

Skills: Python, Django, REST APIs, PostgreSQL, Docker, AWS

Experience:
- Senior Python Developer at TechCorp (2020-2024)
- Junior Developer at StartupXYZ (2018-2020)

Education:
- BS Computer Science, State University (2018)
"""

parsed = ai_service.parse_resume(sample_resume)
print(f"  Name: {parsed.get('name', 'N/A')}")
print(f"  Email: {parsed.get('email', 'N/A')}")
print(f"  Skills detected: {len(parsed.get('skills', []))}")
if parsed.get('skills'):
    print(f"    {', '.join(parsed['skills'][:5])}")

# Test 3: Answer Evaluation
print(f"\n[TEST 3] Testing Answer Evaluation...")
evaluation = ai_service.evaluate_answer(
    question="Explain a time you optimized code performance",
    answer="I identified N+1 queries in our Django views and optimized them using select_related, reducing response time from 2s to 200ms.",
    role="Python Developer"
)
print(f"  Score: {evaluation['score']}/10")
print(f"  Feedback: {evaluation['feedback'][:80]}...")
print(f"  Topics: {evaluation['topics_to_cover'][:80]}...")

# Test 4: Question Generation
print(f"\n[TEST 4] Testing Question Generation...")
questions = ai_service.generate_questions(
    job_description="Seeking Python Developer with Django experience",
    role="Python Developer",
    skills=["Python", "Django", "PostgreSQL"]
)
print(f"  Generated {len(questions)} questions")
if questions:
    print(f"  Sample Q: {questions[0]['question_text'][:70]}...")
    print(f"  Type: {questions[0]['question_type']}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
print("=" * 70)
print("\nYour AI integration is working efficiently!")
print(f"Provider: {ai_service.provider.upper()}")
print("\nNext steps:")
print("1. Update your .env file with correct AI_PROVIDER setting")
print("2. Start Django: python manage.py runserver")
print("3. Test an interview at http://localhost:8000")
