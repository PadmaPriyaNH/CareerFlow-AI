import requests
import json
import re
from typing import Dict, List, Optional, Any, Union
from django.conf import settings


class OllamaEngine:
    """AI Engine for Resume Parsing, Question Generation, and Answer Evaluation
    Hardened to ensure predictable outputs and graceful degradation when the LLM
    responses are not perfectly formatted as JSON.
    """

    def __init__(self):
        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL

    def _send_prompt(self, prompt: str, timeout: int = 30) -> str:
        """Send prompt to Ollama and get response body as text. Returns raw text.
        
        Args:
            prompt: The prompt to send
            timeout: Request timeout in seconds (default 30)
            
        Returns:
            Response text or error message
        """
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # lower temperature for more deterministic JSON
                        "num_predict": 2048,
                    },
                },
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.Timeout:
            return f"Error: Ollama service timeout (no response within {timeout}s)"
        except requests.exceptions.ConnectionError:
            return f"Error: Cannot connect to Ollama at {self.host}"
        except Exception as e:
            return f"Error: {str(e)}"

    # ------------------------ JSON utilities ------------------------
    @staticmethod
    def _extract_json_block(text: str) -> Optional[str]:
        """Try to extract a JSON object/array substring from arbitrary text.
        Returns the JSON substring or None.
        """
        if not text:
            return None
        # Prefer object {...} otherwise array [...]
        obj_start = text.find("{")
        obj_end = text.rfind("}")
        arr_start = text.find("[")
        arr_end = text.rfind("]")

        candidates: List[str] = []
        if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
            candidates.append(text[obj_start : obj_end + 1])
        if arr_start != -1 and arr_end != -1 and arr_end > arr_start:
            candidates.append(text[arr_start : arr_end + 1])

        for c in candidates:
            # Light cleanup of common issues
            cleaned = c.strip()
            # Remove trailing commas before closing braces/brackets
            cleaned = re.sub(r",\s*([}\]])", r"\\1", cleaned)
            try:
                json.loads(cleaned)
                return cleaned
            except Exception:
                continue
        return None

    @staticmethod
    def _safe_json_loads(text: str) -> Optional[Union[Dict[str, Any], List[Any]]]:
        try:
            return json.loads(text)
        except Exception:
            return None

    # ------------------------ Business logic ------------------------
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Extract structured data from resume text. Always returns a dict with keys.
        Keys: name, email, phone, skills (list[str]), experience (list[dict]), education (list[dict])
        """
        base: Dict[str, Any] = {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": [],
            "education": [],
        }
        if not resume_text:
            return base

        prompt = f"""
You are a strict JSON generator resume parser. Extract the following information and return ONLY valid JSON (no prose):
{{
  "name": "full name",
  "email": "email address",
  "phone": "phone number",
  "skills": ["list", "of", "skills"],
  "experience": [{{"company": "", "role": "", "duration": ""}}],
  "education": [{{"degree": "", "institution": "", "year": ""}}]
}}

Resume Text:
{resume_text}

Return ONLY JSON. Do not include backticks or explanations.
"""
        response = self._send_prompt(prompt)
        json_block = self._extract_json_block(response)
        data = self._safe_json_loads(json_block) if json_block else None

        if isinstance(data, dict):
            # Normalize skills to list[str]
            skills = data.get("skills", [])
            if isinstance(skills, str):
                skills = [s.strip() for s in re.split(r",|\n|;", skills) if s.strip()]
            elif not isinstance(skills, list):
                skills = []
            else:
                skills = [str(s).strip() for s in skills if str(s).strip()]

            # Experience/education normalization
            experience = data.get("experience", [])
            if not isinstance(experience, list):
                experience = []
            education = data.get("education", [])
            if not isinstance(education, list):
                education = []

            base.update(
                {
                    "name": str(data.get("name", ""))[:200],
                    "email": str(data.get("email", ""))[:200],
                    "phone": str(data.get("phone", ""))[:50],
                    "skills": skills,
                    "experience": experience,
                    "education": education,
                }
            )
        return base

    def generate_questions(self, job_description: str, role: str, skills: List[str]) -> List[Dict[str, Any]]:
        """Generate 10 interview questions (5 technical + 5 behavioral).
        Always returns a list of dicts with keys: question_text, question_type, order
        """
        skills_str = ", ".join(skills) if skills else "general"
        prompt = f"""
You are a strict JSON generator for interview questions.

Job Description:\n{job_description}\n
Target Role: {role}
Candidate Skills: {skills_str}

Generate exactly 10 interview questions as valid JSON only:
{{
  "technical": ["question 1", "question 2", "question 3", "question 4", "question 5"],
  "behavioral": ["question 1", "question 2", "question 3", "question 4", "question 5"]
}}

Return ONLY JSON. Do not add any extra text.
"""
        response = self._send_prompt(prompt)
        json_block = self._extract_json_block(response)
        data = self._safe_json_loads(json_block) if json_block else None

        def default_questions() -> List[Dict[str, Any]]:
            base_qs: List[str] = [
                f"Explain a challenging problem you solved related to {role}.",
                f"Describe your experience with {skills[0]}" if skills else f"Describe a key skill for {role}.",
                f"How do you ensure code quality and testing?",
                f"Discuss a system design decision you made and why.",
                f"How do you stay current with industry best practices?",
            ]
            beh_qs: List[str] = [
                "Tell me about a time you worked in a team to overcome a challenge.",
                "Describe a situation where you had to resolve a conflict.",
                "Give an example of when you adapted to significant change.",
                "How do you handle tight deadlines and pressure?",
                "Tell me about a time you received critical feedback and what you did.",
            ]
            out: List[Dict[str, Any]] = []
            order = 1
            for q in base_qs:
                out.append({"question_text": q, "question_type": "technical", "order": order})
                order += 1
            for q in beh_qs:
                out.append({"question_text": q, "question_type": "behavioral", "order": order})
                order += 1
            return out

        try:
            technical: List[str] = []
            behavioral: List[str] = []
            if isinstance(data, dict):
                t_raw = data.get("technical", [])
                b_raw = data.get("behavioral", [])
                if isinstance(t_raw, list):
                    technical = [str(x).strip() for x in t_raw if str(x).strip()][:5]
                if isinstance(b_raw, list):
                    behavioral = [str(x).strip() for x in b_raw if str(x).strip()][:5]

            if len(technical) < 5 or len(behavioral) < 5:
                return default_questions()

            questions: List[Dict[str, Any]] = []
            order = 1
            for q in technical[:5]:
                questions.append({"question_text": q, "question_type": "technical", "order": order})
                order += 1
            for q in behavioral[:5]:
                questions.append({"question_text": q, "question_type": "behavioral", "order": order})
                order += 1
            return questions
        except Exception:
            return default_questions()

    def evaluate_answer(self, question: str, answer: str, role: str) -> Dict[str, Any]:
        """Evaluate user's answer and provide feedback. Returns dict with keys:
        score (0-10 int), feedback (str), topics_to_cover (str)
        """
        prompt = f"""
You are an expert interviewer. Evaluate the candidate's answer strictly as JSON (no extra text):
{{
  "score": 7,  // integer 0-10
  "feedback": "Detailed feedback on what was good and what needs improvement",
  "topics_to_cover": ["topic A", "topic B"]
}}

Role: {role}
Question:\n{question}
Candidate's Answer:\n{answer}

Return ONLY JSON. Do not include backticks or explanations.
"""
        response = self._send_prompt(prompt)
        json_block = self._extract_json_block(response)
        data = self._safe_json_loads(json_block) if json_block else None

        score = 5
        feedback = "No feedback available"
        topics_out: Union[str, List[str]] = []

        if isinstance(data, dict):
            # Score normalization
            try:
                score_val = int(round(float(data.get("score", 5))))
                score = max(0, min(10, score_val))
            except Exception:
                score = 5

            feedback = str(data.get("feedback", feedback))

            topics = data.get("topics_to_cover", [])
            if isinstance(topics, list):
                topics_list = [str(t).strip() for t in topics if str(t).strip()]
                topics_out = ", ".join(topics_list)
            elif isinstance(topics, str):
                topics_out = topics.strip()

        return {
            "score": score,
            "feedback": feedback,
            "topics_to_cover": topics_out if isinstance(topics_out, str) else ", ".join(topics_out),
        }

    def is_available(self, timeout: int = 5) -> bool:
        """Quick health check for the Ollama host (used by tests/monitoring)."""
        try:
            resp = requests.get(f"{self.host}/api/models", timeout=timeout)
            return resp.status_code == 200
        except Exception:
            return False


# Global instance
ollama_engine = OllamaEngine()
