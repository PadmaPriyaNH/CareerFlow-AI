from django.contrib import admin
from .models import InterviewSession, Question, Answer
from django.db.models import Avg


# Answer has a OneToOne to Question (no direct FK to InterviewSession), so use it inline with QuestionAdmin only.
class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 0
    readonly_fields = ('user_response', 'ai_score', 'ai_feedback', 'topics_to_cover', 'answered_at')
    can_delete = False


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    readonly_fields = ('question_text', 'question_type', 'order')
    can_delete = False


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'role_title', 'status', 'overall_score', 'created_at', 'question_count')
    list_filter = ('status', 'created_at', 'role_title')
    search_fields = ('user__username', 'role_title', 'job_description')
    readonly_fields = ('user', 'created_at', 'completed_at', 'overall_score')
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('session', 'question_type', 'order', 'get_username')
    list_filter = ('question_type', 'session__status')
    search_fields = ('question_text', 'session__user__username')
    inlines = [AnswerInline]

    def get_username(self, obj):
        return obj.session.user.username

    get_username.short_description = 'User'



@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'ai_score', 'is_voice', 'answered_at')
    list_filter = ('ai_score', 'is_voice', 'answered_at')
    search_fields = ('user_response', 'ai_feedback')
    readonly_fields = ('question', 'user_response', 'is_voice', 'answered_at')
    fields = ('question', 'user_response', 'is_voice', 'ai_score', 'ai_feedback', 'topics_to_cover', 'answered_at')


admin.site.site_header = "CareerFlow AI Admin"
admin.site.site_title = "CareerFlow AI | Admin Portal"
admin.site.index_title = "Welcome to CareerFlow AI Administration"
