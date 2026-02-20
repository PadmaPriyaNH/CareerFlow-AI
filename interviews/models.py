from typing import Dict, List, Optional

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import PyPDF2
from docx import Document
import logging

logger = logging.getLogger(__name__)


class InterviewSession(models.Model):
    STATUS_CHOICES = [
        ('setup', 'Setup'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_description = models.TextField()
    role_title = models.CharField(max_length=200)
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='setup')
    overall_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role_title}"

    def extract_resume_text(self) -> str:
        """Extract and normalize text from uploaded resume (PDF or DOCX)"""
        if not self.resume:
            return ""

        text = ""
        file_path = self.resume.path

        if file_path.lower().endswith('.pdf'):
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text() or ''
                        text += extracted + "\n"
            except Exception:
                # Graceful fallback
                text = ""
        elif file_path.lower().endswith('.docx'):
            try:
                doc = Document(file_path)
                for para in doc.paragraphs:
                    text += (para.text or '') + "\n"
            except Exception:
                text = ""

        # Normalize whitespace and limit size for prompt efficiency
        text = ' '.join(text.split())
        return text[:3500]

    def parse_and_save_resume(self) -> Dict:
        """Parse resume and return extracted data"""
        # Import here to avoid circular imports at import time
        from interviews.services.ai_service import ai_service

        resume_text = self.extract_resume_text()
        parsed_data = ai_service.parse_resume(resume_text)
        return parsed_data

    def _get_default_questions(self) -> List[Dict]:
        """Generate default interview questions when AI is unavailable.
        
        Returns a list of dicts with: question_text, question_type, order
        """
        role = self.role_title or 'Software Engineer'
        
        # Build a generic skill list from text if available
        text = (self.extract_resume_text() + ' ' + self.job_description + ' ' + self.role_title).lower()
        
        # Default technical questions tailored to role
        tech_questions = [
            f"Describe a challenging technical problem you've solved and your approach to it.",
            f"How do you ensure code quality, testing, and maintainability in your projects?",
            f"Explain a system design decision you made and the trade-offs you considered.",
            f"Walk us through your experience with version control and collaboration practices.",
            f"How do you stay current with new technologies and best practices in {role}?"
        ]
        
        # Default behavioral questions
        beh_questions = [
            "Tell me about a time you worked in a team to solve a difficult problem. What was your role?",
            "Describe a situation where you had to resolve a conflict with a colleague or manager.",
            "Give an example of a time you had to adapt to significant change. How did you handle it?",
            "How do you prioritize tasks and handle tight deadlines with competing priorities?",
            "Tell me about a time you received critical feedback. How did you respond and grow from it?"
        ]
        
        questions_data = []
        order = 1
        
        for q in tech_questions:
            questions_data.append({
                'question_text': q,
                'question_type': 'technical',
                'order': order
            })
            order += 1
        
        for q in beh_questions:
            questions_data.append({
                'question_text': q,
                'question_type': 'behavioral',
                'order': order
            })
            order += 1
        
        return questions_data


    def generate_interview_questions(self) -> List['Question']:
        """Generate questions directly based on JD, Role, and Resume with full context.
        
        Sends all information (job description, role, resume text) to AI at once
        for highly personalized and relevant questions.
        
        Handles graceful degradation if AI is unavailable, using default questions.
        """
        from interviews.services.ai_service import ai_service

        # Get resume text
        resume_text = self.extract_resume_text()

        # Extract skills for context (optional, AI will focus on full context)
        skills = []
        try:
            resume_data = self.parse_and_save_resume()
            skills = resume_data.get('skills', []) if isinstance(resume_data, dict) else []
        except Exception:
            # If AI parsing fails, deterministic fallback
            pass

        # Deterministic fallback skill extraction if resume parsing failed
        if not skills:
            text = (resume_text + ' ' + self.job_description + ' ' + self.role_title).lower()
            common_skills = [
                'python','django','flask','fastapi','javascript','typescript','react','vue','angular',
                'node','express','postgres','mysql','sqlite','mongodb','redis','docker','kubernetes',
                'aws','azure','gcp','git','linux','rest','graphql','pytest','unittest','pandas','numpy',
                'ml','machine learning','nlp','data engineering','devops','terraform','ansible'
            ]
            detected = []
            for s in common_skills:
                if s in text:
                    detected.append(s)
            skills = list(dict.fromkeys(detected))[:10]

        try:
            # Use new direct context-based generation
            questions_data = ai_service.generate_questions_from_context(
                job_description=self.job_description,
                role=self.role_title,
                resume_text=resume_text,
                parsed_skills=skills
            )
        except Exception as e:
            logger.error(f"Error generating questions with context: {e}")
            # If question generation fails, use default questions
            questions_data = self._get_default_questions()

        created_questions: List[Question] = []
        for q_data in questions_data:
            question = Question.objects.create(
                session=self,
                question_text=q_data.get('question_text', 'Question'),
                question_type=q_data.get('question_type', 'technical'),
                order=int(q_data.get('order', 0)),
            )
            created_questions.append(question)

        if created_questions:
            self.status = 'in_progress'
            self.save(update_fields=['status'])

        return created_questions

    def get_next_unanswered_question(self) -> Optional['Question']:
        """Get the next question that hasn't been answered"""
        answered_ids = Answer.objects.filter(question__session=self).values_list('question_id', flat=True)
        return self.questions.exclude(id__in=answered_ids).order_by('order').first()

    def calculate_overall_score(self) -> float:
        """Calculate average score from all answers and mark completed"""
        answers = Answer.objects.filter(question__session=self)
        if answers.exists():
            self.overall_score = sum(a.ai_score for a in answers) / answers.count()
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save(update_fields=['overall_score', 'status', 'completed_at'])
        return float(self.overall_score)


class Question(models.Model):
    TYPE_CHOICES = [
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
    ]

    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.question_text[:50]


class Answer(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    user_response = models.TextField()
    is_voice = models.BooleanField(default=False)
    ai_score = models.IntegerField(default=0)
    ai_feedback = models.TextField()
    topics_to_cover = models.TextField(blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer for {self.question_id}"
