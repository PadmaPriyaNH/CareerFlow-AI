
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from .models import InterviewSession, Question, Answer
from .forms import InterviewSetupForm

@login_required
@require_POST
def stop_interview(request, session_id):
    """Stop the interview and redirect to summary page."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    session.status = 'completed'
    session.completed_at = timezone.now()
    session.save()
    session.calculate_overall_score()
    return redirect('interview_feedback', session_id=session.id)


@login_required
def interview_setup(request):
    """Page to setup new interview (JD, Role, Resume Upload)"""
    if request.method == 'POST':
        form = InterviewSetupForm(request.POST, request.FILES)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()

            # Check if Ollama is available before generating questions
            from interviews.services.ollama_engine import ollama_engine
            if not ollama_engine.is_available():
                messages.warning(request, 
                    "⚠️ AI service is unavailable. Using default questions for this session. "
                    "Please ensure Ollama is running at the configured address for personalized questions.")
                # Generate default questions as fallback
                session.generate_interview_questions()
            else:
                # Generate questions with AI personalization
                try:
                    session.generate_interview_questions()
                    messages.success(request, "Interview setup complete! Starting AI-powered questions...")
                except Exception as e:
                    messages.warning(request, 
                        f"Interview started with default questions: {type(e).__name__}. "
                        "Please check your Ollama connection.")
                    # Session already has status=setup, will use default questions
            
            return redirect('interview_room', session_id=session.id)
    else:
        form = InterviewSetupForm()

    return render(request, 'interviews/setup.html', {'form': form})


@login_required
def interview_room(request, session_id):
    """Main interview room with one question at a time"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

    if session.status == 'setup':
        try:
            session.generate_interview_questions()
        except Exception as e:
            # If question generation fails, show error and redirect to setup to retry
            messages.error(request, f"Failed to generate questions: {str(e)}. Please try again.")
            return redirect('interview_setup')

    current_question = session.get_next_unanswered_question()

    if not current_question:
        # No questions available - session is complete
        session.calculate_overall_score()
        return redirect('interview_feedback', session_id=session.id)

    answered = Answer.objects.filter(question__session=session).order_by('question__order')

    return render(request, 'interviews/room.html', {
        'session': session,
        'current_question': current_question,
        'answered': answered,
        'progress': (answered.count() / session.questions.count()) * 100 if session.questions.count() > 0 else 0
    })


@require_POST
@login_required
def submit_answer(request, session_id, question_id):
    """Submit answer and get AI evaluation. Supports HTMX and JSON."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    question = get_object_or_404(Question, id=question_id, session=session)

    user_response = request.POST.get('answer', '')
    is_voice = request.POST.get('is_voice', 'false') == 'true'

    if not user_response:
        if request.META.get('HTTP_HX_REQUEST'):
            return HttpResponse('<div class="alert alert-danger">No answer provided</div>', status=400)
        return JsonResponse({'error': 'No answer provided'}, status=400)

    # Use existing engine; check availability for graceful degradation
    from interviews.services.ollama_engine import ollama_engine
    if not ollama_engine.is_available():
        # Create a neutral answer with default scoring so the session can progress even if AI is down
        Answer.objects.create(
            question=question,
            user_response=user_response,
            is_voice=is_voice,
            ai_score=5,
            ai_feedback='AI service unavailable; recorded your answer without AI evaluation.',
            topics_to_cover='',
        )
        next_question = session.get_next_unanswered_question()
        if next_question:
            return JsonResponse({
                'success': True,
                'score': 5,
                'feedback': 'AI service unavailable; recorded your answer without AI evaluation.',
                'topics': '',
                'next_question': next_question.question_text,
                'next_question_id': next_question.id,
                'question_type': next_question.question_type,
                'progress': (Answer.objects.filter(question__session=session).count() / session.questions.count()) * 100 if session.questions.count() else 0
            })
        else:
            session.calculate_overall_score()
            return JsonResponse({
                'success': True,
                'score': 5,
                'feedback': 'AI service unavailable; finalizing without evaluation.',
                'complete': True,
                'redirect_url': f'/interview/{session.id}/feedback/'
            })

    evaluation = ollama_engine.evaluate_answer(
        question.question_text,
        user_response,
        session.role_title
    )

    Answer.objects.create(
        question=question,
        user_response=user_response,
        is_voice=is_voice,
        ai_score=evaluation.get('score', 5),
        ai_feedback=evaluation.get('feedback', 'No feedback available'),
        topics_to_cover=evaluation.get('topics_to_cover', ''),
    )

    next_question = session.get_next_unanswered_question()

    # HTMX response path: return HTML snippet for chat-like UX
    if request.META.get('HTTP_HX_REQUEST'):
        feedback_html = f"""
        <div class=\"mt-3\">
          <div class=\"alert alert-info\">
            <strong>Score: {evaluation.get('score', 5)}/10</strong>
            <p>{evaluation.get('feedback', '')}</p>
            <hr/>
            <strong>Topics to Cover:</strong>
            <p>{evaluation.get('topics_to_cover', '')}</p>
          </div>
        </div>
        """
        if next_question:
            question_html = f"""
            <div class=\"card mt-3\">
              <div class=\"card-header\">
                <span class=\"badge bg-{'primary' if next_question.question_type == 'technical' else 'success'}\">{next_question.question_type.title()}</span>
                Question {next_question.order}
              </div>
              <div class=\"card-body\">
                <h5 class=\"card-title\">{next_question.question_text}</h5>
                <form hx-post=\"/interview/{session.id}/submit/{next_question.id}/\" hx-target=\"#chat-thread\" hx-swap=\"beforeend\">
                                    <div class=\"mb-3\">
                    <textarea class=\"form-control\" name=\"answer\" rows=\"5\" placeholder=\"Type your answer here...\"></textarea>
                  </div>
                  <button type=\"submit\" class=\"btn btn-primary\">Submit Answer</button>
                </form>
              </div>
            </div>
            """
            return HttpResponse(feedback_html + question_html)
        else:
            # Completed: provide link to feedback
            complete_html = f"""
            {feedback_html}
            <div class=\"mt-3\">
              <a href=\"/interview/{session.id}/feedback/\" class=\"btn btn-success\">View Final Report</a>
            </div>
            """
            return HttpResponse(complete_html)

    # JSON path (non-HTMX)
    if next_question:
        return JsonResponse({
            'success': True,
            'score': evaluation.get('score', 5),
            'feedback': evaluation.get('feedback', ''),
            'topics': evaluation.get('topics_to_cover', ''),
            'next_question': next_question.question_text,
            'next_question_id': next_question.id,
            'question_type': next_question.question_type,
            'progress': (Answer.objects.filter(question__session=session).count() / session.questions.count()) * 100
        })
    else:
        session.calculate_overall_score()
        return JsonResponse({
            'success': True,
            'score': evaluation.get('score', 5),
            'feedback': evaluation.get('feedback', ''),
            'complete': True,
            'redirect_url': f'/interview/{session.id}/feedback/'
        })


@login_required
def stop_interview(request, session_id):
    """Stop the interview early, compute overall score, and redirect to feedback."""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    # Compute score from any answers so far and mark completed
    session.calculate_overall_score()
    session.status = 'completed'
    if not session.completed_at:
        session.completed_at = timezone.now()
    session.save(update_fields=['status', 'completed_at', 'overall_score'])
    return redirect('interview_feedback', session_id=session.id)


@login_required
def interview_feedback(request, session_id):
    """Show final feedback and scorecard"""
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answers = Answer.objects.filter(question__session=session).order_by('question__order')

    return render(request, 'interviews/feedback.html', {
        'session': session,
        'answers': answers
    })
