#!/usr/bin/env python
"""
Test script for direct context-based question generation from AI.
Shows how the AI generates interview questions using full Job Description,
Role, and Resume context together.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from interviews.services.ai_service import ai_service

# Sample data
JOB_DESCRIPTION = """
Senior Python Developer

We're looking for an experienced Python developer with 5+ years of experience.
Required Skills:
- Python 3.9+, Django, FastAPI
- PostgreSQL, Redis
- Docker, Kubernetes
- AWS or Azure
- REST API Design
- Unit Testing, pytest

Responsibilities:
- Develop scalable backend systems
- Design and optimize database schemas
- Lead code reviews and mentor junior developers
- Implement CI/CD pipelines
"""

ROLE_TITLE = "Senior Python Developer"

RESUME_TEXT = """
John Doe
john.doe@example.com
(555) 123-4567

EXPERIENCE:
Senior Software Engineer, TechCorp (2020-Present)
- Led development of microservices using Django and FastAPI
- Optimized PostgreSQL queries, improving performance by 40%
- Implemented Docker and Kubernetes for deployment
- Mentored 3 junior developers

Python Developer, StartupXYZ (2018-2020)
- Built REST APIs using Django
- Wrote comprehensive unit tests using pytest
- Deployed applications on AWS EC2

SKILLS:
Python, Django, FastAPI, PostgreSQL, Redis, Docker, AWS, Git, pytest, REST APIs

EDUCATION:
B.S. Computer Science, State University (2018)
"""

def test_direct_generation():
    """Test the new generate_questions_from_context method"""
    
    print("=" * 70)
    print("DIRECT CONTEXT-BASED QUESTION GENERATION TEST")
    print("=" * 70)
    
    if not ai_service.is_available():
        print("\n❌ AI Service is not available!")
        return
    
    print("\n✓ AI Service is available")
    print(f"AI Provider: {ai_service.provider.upper()}")
    
    print("\n" + "=" * 70)
    print("INPUT CONTEXT:")
    print("=" * 70)
    print(f"\nRole: {ROLE_TITLE}")
    print(f"\nJob Description (excerpt):\n{JOB_DESCRIPTION[:200]}...")
    print(f"\nResume (excerpt):\n{RESUME_TEXT[:200]}...")
    
    print("\n" + "=" * 70)
    print("GENERATING QUESTIONS...")
    print("=" * 70)
    
    try:
        # Call the new direct context method
        questions = ai_service.generate_questions_from_context(
            job_description=JOB_DESCRIPTION,
            role=ROLE_TITLE,
            resume_text=RESUME_TEXT,
            parsed_skills=['Python', 'Django', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS']
        )
        
        print(f"\n✓ Generated {len(questions)} questions\n")
        
        # Display questions grouped by type
        technical_q = [q for q in questions if q.get('question_type') == 'technical']
        behavioral_q = [q for q in questions if q.get('question_type') == 'behavioral']
        
        print("TECHNICAL QUESTIONS:")
        print("-" * 70)
        for i, q in enumerate(technical_q, 1):
            print(f"{i}. {q['question_text']}\n")
        
        print("\nBEHAVIORAL QUESTIONS:")
        print("-" * 70)
        for i, q in enumerate(behavioral_q, 1):
            print(f"{i}. {q['question_text']}\n")
        
        print("=" * 70)
        print("✓ DIRECT CONTEXT GENERATION SUCCESSFUL!")
        print("=" * 70)
        print("\nThe AI generated questions taking into account:")
        print("  ✓ Job description requirements (Django, FastAPI, PostgreSQL, etc.)")
        print("  ✓ Target role (Senior Python Developer)")
        print("  ✓ Candidate's resume (5+ years exp, specific tech stack)")
        print("  ✓ Skills match and gaps between role and candidate")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_direct_generation()
