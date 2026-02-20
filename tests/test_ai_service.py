#!/usr/bin/env python
"""
AI Service Tests - Comprehensive verification of AI functionality

Tests:
- Provider availability and health checks
- Resume parsing and extraction
- Answer evaluation with scoring
- Question generation from job description + role + resume
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from interviews.services.ai_service import ai_service


def test_provider_availability():
    """Test if AI provider (Groq/Ollama) is available"""
    print("\n" + "=" * 70)
    print("[TEST 1] AI Service Availability")
    print("=" * 70)
    
    is_available = ai_service.is_available()
    
    if is_available:
        print(f"✓ AI Provider: {ai_service.provider.upper()}")
        print("✓ Status: AVAILABLE")
        return True
    else:
        print(f"✗ AI Provider: {ai_service.provider.upper()}")
        print("✗ Status: UNAVAILABLE")
        print("  Please check your GROQ_API_KEY or Ollama service")
        return False


def test_resume_parsing():
    """Test resume parsing functionality"""
    print("\n" + "=" * 70)
    print("[TEST 2] Resume Parsing")
    print("=" * 70)
    
    sample_resume = """
    John Doe
    john.doe@example.com
    (555) 123-4567
    
    EXPERIENCE:
    Senior Python Developer, TechCorp (2020-Present)
    - Built microservices with Django and FastAPI
    - Optimized PostgreSQL queries
    - Led Docker and Kubernetes deployments
    
    SKILLS: Python, Django, FastAPI, PostgreSQL, Docker, AWS, Git
    """
    
    try:
        result = ai_service.parse_resume(sample_resume)
        
        if result and isinstance(result, dict):
            print(f"✓ Name: {result.get('name', 'N/A')}")
            print(f"✓ Email: {result.get('email', 'N/A')}")
            print(f"✓ Phone: {result.get('phone', 'N/A')}")
            
            skills = result.get('skills', [])
            if skills:
                print(f"✓ Skills detected: {len(skills)}")
                print(f"  {', '.join(skills[:5])}")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return False


def test_answer_evaluation():
    """Test answer evaluation with scoring"""
    print("\n" + "=" * 70)
    print("[TEST 3] Answer Evaluation")
    print("=" * 70)
    
    question = "Explain how you optimized database performance in a production system"
    answer = "I analyzed slow queries using EXPLAIN ANALYZE, added indexes on frequently queried columns, and implemented query caching with Redis, improving response time from 2s to 200ms."
    role = "Senior Backend Engineer"
    
    try:
        result = ai_service.evaluate_answer(question, answer, role)
        
        if result:
            score = result.get('score', 0)
            feedback = result.get('feedback', '')[:100]
            
            print(f"✓ Score: {score}/10")
            print(f"✓ Feedback: {feedback}...")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return False


def test_question_generation():
    """Test question generation"""
    print("\n" + "=" * 70)
    print("[TEST 4] Question Generation")
    print("=" * 70)
    
    questions_data = ai_service.generate_questions(
        job_description="Senior Python Developer with Django/FastAPI/PostgreSQL",
        role="Senior Python Developer",
        skills=["Python", "Django", "PostgreSQL", "Docker", "AWS"]
    )
    
    try:
        if questions_data and len(questions_data) >= 10:
            technical = [q for q in questions_data if q.get('question_type') == 'technical']
            behavioral = [q for q in questions_data if q.get('question_type') == 'behavioral']
            
            print(f"✓ Generated {len(questions_data)} questions")
            print(f"✓ Technical: {len(technical)}")
            print(f"✓ Behavioral: {len(behavioral)}")
            
            if technical:
                print(f"  Sample: {technical[0]['question_text'][:80]}...")
            
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return False


def test_direct_context_generation():
    """Test direct context-based question generation"""
    print("\n" + "=" * 70)
    print("[TEST 5] Direct Context-Based Question Generation")
    print("=" * 70)
    
    job_description = """
    Senior Python Developer
    5+ years required
    Django, FastAPI, PostgreSQL, Docker, Kubernetes
    """
    
    resume_text = """
    John Doe - Senior Engineer
    5 years Python, Django/FastAPI
    PostgreSQL optimization, Docker, AWS
    """
    
    try:
        questions = ai_service.generate_questions_from_context(
            job_description=job_description,
            role="Senior Python Developer",
            resume_text=resume_text,
            parsed_skills=["Python", "Django", "PostgreSQL", "Docker", "AWS"]
        )
        
        if questions and len(questions) >= 10:
            print(f"✓ Generated {len(questions)} context-specific questions")
            technical = [q for q in questions if q.get('question_type') == 'technical']
            behavioral = [q for q in questions if q.get('question_type') == 'behavioral']
            print(f"✓ Technical: {len(technical)}, Behavioral: {len(behavioral)}")
            return True
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return False


def run_all_tests():
    """Run all tests and summarize"""
    print("\n" + "=" * 70)
    print("CAREERFLOW AI - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    results = {
        "Provider Availability": test_provider_availability(),
        "Resume Parsing": test_resume_parsing(),
        "Answer Evaluation": test_answer_evaluation(),
        "Question Generation": test_question_generation(),
        "Direct Context Generation": test_direct_context_generation(),
    }
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print("\n" + "=" * 70)
    if total_passed == total_tests:
        print(f"✓ ALL {total_tests} TESTS PASSED!")
    else:
        print(f"✗ {total_passed}/{total_tests} tests passed")
    print("=" * 70)
    
    return all(results.values())


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
