"""
AI Service - Provider-agnostic AI interface supporting Groq and Ollama
"""
import os
import json
import re
from typing import Dict, Any, Optional, Union, List
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)


class AIService:
    """
    Unified AI service that supports multiple providers (Groq, Ollama).
    Automatically selects provider based on AI_PROVIDER env variable.
    """

    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "groq").lower()
        self.temperature = 0.5
        self.max_tokens = 256

        if self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                logger.warning("GROQ_API_KEY not set. Falling back to Ollama.")
                self.provider = "ollama"
            else:
                self.llm = ChatGroq(
                    api_key=api_key,
                    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=90,  # Allow up to 90 seconds
                )
                logger.info(f"Initialized ChatGroq with model: {os.getenv('GROQ_MODEL')}")

        if self.provider == "ollama":
            self.llm = ChatOllama(
                base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                model=os.getenv("OLLAMA_MODEL", "mistral"),
                temperature=self.temperature,
                num_predict=256,
            )
            logger.info(
                f"Initialized ChatOllama with model: {os.getenv('OLLAMA_MODEL')}"
            )

    def is_available(self) -> bool:
        """Check if AI service is available and responding."""
        try:
            if self.provider == "groq":
                # Quick test call to Groq
                response = self.llm.invoke([HumanMessage(content="hi")])
                return bool(response and response.content)
            else:  # ollama
                # Test Ollama health endpoint
                import requests

                resp = requests.get(
                    f"{os.getenv('OLLAMA_HOST', 'http://localhost:11434')}/api/tags",
                    timeout=5,
                )
                return resp.status_code == 200
        except Exception as e:
            logger.error(f"AI service availability check failed: {e}")
            return False

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from text response."""
        if not text:
            return None

        # Try to find JSON object
        obj_start = text.find("{")
        obj_end = text.rfind("}")

        if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
            json_str = text[obj_start : obj_end + 1]
            # Clean up common issues
            json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        return None

    def evaluate_answer(
        self, question: str, answer: str, role: str
    ) -> Dict[str, Any]:
        """
        Evaluate an interview answer and return score, feedback, and topics.

        Args:
            question: The interview question
            answer: The candidate's answer
            role: The role being interviewed for

        Returns:
            Dict with keys: score (0-10), feedback (str), topics_to_cover (str)
        """
        # Simplified prompt for faster generation
        prompt = f"""Evaluate this interview answer. Return ONLY JSON:
{{"score": 7, "feedback": "Brief feedback", "topics_to_cover": ["topic1"]}}

Role: {role}
Q: {question}
A: {answer}"""

        try:
            messages = [
                SystemMessage(
                    content="You are an expert interviewer. Return only valid JSON, no extra text."
                ),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            response_text = response.content

            # Extract JSON from response
            data = self._extract_json_from_text(response_text)

            if isinstance(data, dict):
                # Normalize score
                try:
                    score = int(round(float(data.get("score", 6))))
                    score = max(0, min(10, score))
                except (ValueError, TypeError):
                    score = 6

                feedback = str(data.get("feedback", "Good effort. Keep practicing."))
                topics = data.get("topics_to_cover", [])

                if isinstance(topics, list):
                    topics_str = ", ".join(str(t) for t in topics)
                elif isinstance(topics, str):
                    topics_str = topics
                else:
                    topics_str = "Review the question and think about edge cases."

                return {
                    "score": score,
                    "feedback": feedback,
                    "topics_to_cover": topics_str,
                }
        except Exception as e:
            logger.error(f"Error evaluating answer: {e}")

        # Fallback response if evaluation fails
        return {
            "score": 6,
            "feedback": "Recorded your answer. Try again for evaluation.",
            "topics_to_cover": "Continue with the next question.",
        }

    def generate_questions(
        self, job_description: str, role: str, skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on job description, role, and skills.

        Args:
            job_description: Job description text
            role: Role title
            skills: List of candidate skills

        Returns:
            List of dicts with keys: question_text, question_type, order
        """
        skills_str = ", ".join(skills[:5]) if skills else "general"
        job_desc_short = job_description[:300] if job_description else ""

        prompt = f"""Generate 10 interview questions as JSON (ONLY JSON):
{{"technical": ["q1","q2","q3","q4","q5"], "behavioral": ["q1","q2","q3","q4","q5"]}}

Role: {role}
Skills: {skills_str}
Job: {job_desc_short}"""

        try:
            messages = [
                SystemMessage(
                    content="You are a technical interviewer. Return only valid JSON, no extra text."
                ),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            response_text = response.content

            # Extract JSON from response
            data = self._extract_json_from_text(response_text)

            if isinstance(data, dict):
                technical = data.get("technical", [])
                behavioral = data.get("behavioral", [])

                if isinstance(technical, list) and isinstance(behavioral, list):
                    if len(technical) >= 5 and len(behavioral) >= 5:
                        questions = []
                        order = 1
                        for q in technical[:5]:
                            questions.append(
                                {
                                    "question_text": str(q),
                                    "question_type": "technical",
                                    "order": order,
                                }
                            )
                            order += 1
                        for q in behavioral[:5]:
                            questions.append(
                                {
                                    "question_text": str(q),
                                    "question_type": "behavioral",
                                    "order": order,
                                }
                            )
                            order += 1
                        return questions
        except Exception as e:
            logger.error(f"Error generating questions: {e}")

        # Return default questions if AI fails
        return self._get_default_questions(role)

    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume text and extract structured information.

        Args:
            resume_text: Raw resume text

        Returns:
            Dict with keys: name, email, phone, skills, experience, education
        """
        base = {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": [],
            "education": [],
        }

        if not resume_text:
            return base

        resume_short = resume_text[:400]
        prompt = f"""Extract resume info as JSON (ONLY JSON):
{{"name":"","email":"","phone":"","skills":[],"experience":[],"education":[]}}

Resume: {resume_short}"""

        try:
            messages = [
                SystemMessage(
                    content="Extract information from resume. Return only valid JSON."
                ),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            response_text = response.content

            # Extract JSON from response
            data = self._extract_json_from_text(response_text)

            if isinstance(data, dict):
                # Normalize skills
                skills = data.get("skills", [])
                if isinstance(skills, str):
                    skills = [s.strip() for s in re.split(r",|\n|;", skills) if s.strip()]
                elif isinstance(skills, list):
                    skills = [str(s).strip() for s in skills if str(s).strip()]
                else:
                    skills = []

                base.update(
                    {
                        "name": str(data.get("name", ""))[:200],
                        "email": str(data.get("email", ""))[:200],
                        "phone": str(data.get("phone", ""))[:50],
                        "skills": skills,
                        "experience": data.get("experience", []),
                        "education": data.get("education", []),
                    }
                )
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")

        return base

    def generate_questions_from_context(
        self, job_description: str, role: str, resume_text: str, parsed_skills: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate tailored interview questions directly from full context.
        
        This method sends all information (JD, Role, Resume) to the AI at once,
        allowing it to create highly relevant, personalized questions.

        Args:
            job_description: Full job description text
            role: Target role title
            resume_text: Full extracted resume text
            parsed_skills: Optional pre-extracted skills list

        Returns:
            List of 10 questions (5 technical, 5 behavioral) with context
        """
        # Limit context to avoid token overload
        jd_context = job_description[:500] if job_description else ""
        resume_context = resume_text[:500] if resume_text else ""
        skills_str = ", ".join(parsed_skills[:8]) if parsed_skills else "various technologies"

        prompt = f"""Generate 10 interview questions for this candidate as pure JSON (ONLY):
{{"technical": ["q1","q2","q3","q4","q5"], "behavioral": ["q1","q2","q3","q4","q5"]}}

JOB DESCRIPTION: {jd_context}

TARGET ROLE: {role}

CANDIDATE RESUME: {resume_context}

SKILLS: {skills_str}

Create SPECIFIC questions based on:
1. Required skills from the job description
2. The candidate's experience from resume
3. The role requirements
4. Potential gaps or skill matches"""

        try:
            messages = [
                SystemMessage(
                    content="You are a senior technical interviewer. Generate highly relevant, specific questions based on the job and resume. Return ONLY valid JSON."
                ),
                HumanMessage(content=prompt),
            ]
            response = self.llm.invoke(messages)
            response_text = response.content

            # Extract JSON from response
            data = self._extract_json_from_text(response_text)

            if isinstance(data, dict):
                technical = data.get("technical", [])
                behavioral = data.get("behavioral", [])

                if isinstance(technical, list) and isinstance(behavioral, list):
                    if len(technical) >= 5 and len(behavioral) >= 5:
                        questions = []
                        order = 1
                        for q in technical[:5]:
                            questions.append(
                                {
                                    "question_text": str(q),
                                    "question_type": "technical",
                                    "order": order,
                                }
                            )
                            order += 1
                        for q in behavioral[:5]:
                            questions.append(
                                {
                                    "question_text": str(q),
                                    "question_type": "behavioral",
                                    "order": order,
                                }
                            )
                            order += 1
                        return questions
        except Exception as e:
            logger.error(f"Error generating questions from context: {e}")

        # Return default questions if AI fails
        return self._get_default_questions(role)

    @staticmethod
    def _get_default_questions(role: str) -> List[Dict[str, Any]]:
        """Return default questions when AI fails."""
        questions = [
            {
                "question_text": f"Explain a challenging problem you solved related to {role}.",
                "question_type": "technical",
                "order": 1,
            },
            {
                "question_text": f"Describe your experience with the main technologies for a {role} role.",
                "question_type": "technical",
                "order": 2,
            },
            {
                "question_text": "How do you ensure code quality and testing?",
                "question_type": "technical",
                "order": 3,
            },
            {
                "question_text": "Discuss a system design decision you made and why.",
                "question_type": "technical",
                "order": 4,
            },
            {
                "question_text": "How do you stay current with industry best practices?",
                "question_type": "technical",
                "order": 5,
            },
            {
                "question_text": "Tell me about a time you worked in a team to overcome a challenge.",
                "question_type": "behavioral",
                "order": 6,
            },
            {
                "question_text": "Describe a situation where you had to resolve a conflict.",
                "question_type": "behavioral",
                "order": 7,
            },
            {
                "question_text": "Give an example of when you adapted to significant change.",
                "question_type": "behavioral",
                "order": 8,
            },
            {
                "question_text": "How do you handle tight deadlines and pressure?",
                "question_type": "behavioral",
                "order": 9,
            },
            {
                "question_text": "Tell me about a time you received critical feedback and what you did.",
                "question_type": "behavioral",
                "order": 10,
            },
        ]
        return questions


# Global singleton instance
ai_service = AIService()
