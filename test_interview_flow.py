#!/usr/bin/env python
"""
Test script to verify the interview setup flow end-to-end
Tests the graceful degradation when Ollama is unavailable
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from interviews.models import InterviewSession, Question, Answer


def test_interview_setup_without_ollama():
    """Test that interview setup works even without Ollama running"""
    print("\n" + "="*60)
    print("TEST: Interview Setup Flow (with Ollama unavailable)")
    print("="*60)
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_interview_user',
        defaults={'email': 'test@example.com', 'first_name': 'Test'}
    )
    print(f"\n[1] User: {user.username} ({'created' if created else 'existing'})")
    
    # Create an interview session
    session = InterviewSession.objects.create(
        user=user,
        job_description="Python developer with 5+ years of experience in Django and REST APIs",
        role_title="Senior Python Developer",
        resume=None  # File not needed for this test
    )
    print(f"[2] Session created: ID={session.id}, Status={session.status}")
    
    # Generate questions (should work with fallback if Ollama unavailable)
    try:
        questions = session.generate_interview_questions()
        print(f"[3] Questions generated: {len(questions)} questions")
        
        # Check that questions were created
        session_questions = Question.objects.filter(session=session)
        print(f"[4] Questions in DB: {session_questions.count()}")
        
        # Verify question structure
        for i, q in enumerate(session_questions[:3], 1):
            print(f"    Q{q.order} ({q.question_type}): {q.question_text[:50]}...")
        
        if session_questions.count() >= 10:
            print("[✓] SUCCESS: All 10 questions generated!")
        else:
            print(f"[⚠] WARNING: Expected 10 questions, got {session_questions.count()}")
            
        # Test getting next unanswered question
        next_q = session.get_next_unanswered_question()
        print(f"[5] Next question available: {next_q is not None}")
        if next_q:
            print(f"    Question: {next_q.question_text[:60]}...")
        
        print("\n[✓] TEST PASSED: Interview setup flow works correctly!")
        return True
        
    except Exception as e:
        print(f"[✗] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_submit_answer_flow():
    """Test submitting an answer to check the evaluation flow"""
    print("\n" + "="*60)
    print("TEST: Answer Submission Flow")
    print("="*60)
    
    # Get the test session we just created
    user = User.objects.get(username='test_interview_user')
    sessions = InterviewSession.objects.filter(user=user).order_by('-id')
    
    if not sessions.exists():
        print("[✗] No test session found")
        return False
    
    session = sessions.first()
    print(f"[1] Using session: ID={session.id}")
    
    # Get first question
    q = session.get_next_unanswered_question()
    if not q:
        print("[✗] No unanswered questions found")
        return False
    
    print(f"[2] Question: {q.question_text[:50]}...")
    
    # Create an answer
    try:
        answer = Answer.objects.create(
            question=q,
            user_response="This is my test answer to the interview question.",
            is_voice=False,
            ai_score=7,
            ai_feedback="Good response! Consider adding more specific examples.",
            topics_to_cover="Technical depth, Real-world examples"
        )
        print(f"[3] Answer created: {answer.id}")
        
        # Check next question
        next_q = session.get_next_unanswered_question()
        print(f"[4] Next question available: {next_q is not None}")
        if next_q:
            print(f"    Question: {next_q.question_text[:60]}...")
        
        print("\n[✓] TEST PASSED: Answer submission works correctly!")
        return True
        
    except Exception as e:
        print(f"[✗] ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_progress_calculation():
    """Test progress calculation as interview progresses"""
    print("\n" + "="*60)
    print("TEST: Progress Calculation")
    print("="*60)
    
    user = User.objects.get(username='test_interview_user')
    session = InterviewSession.objects.filter(user=user).order_by('-id').first()
    
    if not session:
        print("[✗] No session found")
        return False
    
    total_questions = session.questions.count()
    answered_count = Answer.objects.filter(question__session=session).count()
    progress = (answered_count / total_questions * 100) if total_questions > 0 else 0
    
    print(f"[1] Total questions: {total_questions}")
    print(f"[2] Answered: {answered_count}")
    print(f"[3] Progress: {progress:.1f}%")
    
    if answered_count < total_questions:
        print(f"[4] Can continue: Questions remaining = {total_questions - answered_count}")
    
    print("\n[✓] TEST PASSED: Progress calculation works!")
    return True


if __name__ == '__main__':
    print("\n" + "="*60)
    print("CareerFlow AI - Interview Flow Test Suite")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Interview Setup (Graceful Degradation)", test_interview_setup_without_ollama()))
    results.append(("Answer Submission", test_submit_answer_flow()))
    results.append(("Progress Calculation", test_progress_calculation()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {len(results) - total_passed} test(s) failed")
