import requests
import json

def ask_mistral(prompt):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False  # Wait for full response
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    # --- TEST 1: Resume Parsing ---
    print("🧪 Testing Resume Parsing...")
    resume_prompt = """
You are a resume parser.
Extract the following information and return ONLY valid JSON:
- full_name
- email
- skills
- education

Resume:
N H Padma Priya
Email: padmapriya0657@gmail.com
Skills: Python, Django, Machine Learning, SQL
Education: B.Sc Computer Science, Maharani Cluster University
"""

    result = ask_mistral(resume_prompt)
    print("✅ Resume Parsing Output:")
    print(result)
    print("\n" + "="*30 + "\n")

    # --- TEST 2: Mock Interview ---
    print("🎤 Testing Mock Interview...")
    interview_prompt = """
You are a technical interviewer.
Candidate skills: Python, Django
Generate 2 easy interview questions.
Return ONLY the questions.
"""

    result = ask_mistral(interview_prompt)
    print("✅ Interview Questions:")
    print(result)