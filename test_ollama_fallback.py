#!/usr/bin/env python
"""Quick test of Ollama engine graceful degradation"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from interviews.services.ollama_engine import ollama_engine

print("\n" + "="*60)
print("Testing Ollama Engine Graceful Degradation")
print("="*60)

print("\n1. Checking Ollama availability...")
is_available = ollama_engine.is_available()
print(f"   Ollama available: {is_available}")

print("\n2. Testing questions generation (should use fallback if unavailable)...")
try:
    qs = ollama_engine.generate_questions(
        'Build scalable Python microservices with Django',
        'Senior Python Developer',
        ['python', 'django', 'docker']
    )
    print(f"   ✓ Generated {len(qs)} questions")
    
    print("\n3. Sample questions:")
    for i, q in enumerate(qs[:5], 1):
        print(f"   Q{i} ({q.get('question_type')}): {q.get('question_text')[:60]}...")
    
    if len(qs) == 10:
        print("\n✓ SUCCESS: All questions generated correctly!")
    else:
        print(f"\n⚠ WARNING: Expected 10 questions, got {len(qs)}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
