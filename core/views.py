
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from interviews.models import InterviewSession
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta

@login_required
def summary(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/summary.html', {'sessions': sessions})


@login_required
def dashboard(request):
    """Dashboard with interview history and statistics"""
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')

    total_interviews = sessions.count()
    completed_interviews = sessions.filter(status='completed').count()

    avg_score = sessions.filter(status='completed').aggregate(Avg('overall_score'))['overall_score__avg']
    avg_score = round(avg_score, 1) if avg_score else 0

    recent_interviews = sessions[:5]

    score_ranges = {
        '0-3': sessions.filter(overall_score__lt=4).count(),
        '4-6': sessions.filter(overall_score__gte=4, overall_score__lt=7).count(),
        '7-8': sessions.filter(overall_score__gte=7, overall_score__lt=9).count(),
        '9-10': sessions.filter(overall_score__gte=9).count(),
    }

    roles = sessions.values('role_title').annotate(count=Count('id')).order_by('-count')[:5]

    week_ago = timezone.now() - timedelta(days=7)
    weekly_activity = sessions.filter(created_at__gte=week_ago).count()

    context = {
        'sessions': sessions,
        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'avg_score': avg_score,
        'recent_interviews': recent_interviews,
        'score_ranges': score_ranges,
        'roles': roles,
        'weekly_activity': weekly_activity,
    }

    return render(request, 'core/dashboard.html', context)
