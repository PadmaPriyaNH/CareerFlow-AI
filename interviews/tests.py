from django.test import TestCase
from unittest.mock import patch, Mock
from .services.ollama_engine import OllamaEngine


def _make_response(text, status=200):
    m = Mock()
    m.status_code = status
    m.json.return_value = {"response": text}
    m.raise_for_status = Mock()
    return m


class OllamaEngineTests(TestCase):

    def test_parse_resume_success(self):
        engine = OllamaEngine()
        sample_json = '{"name":"Alice","email":"alice@example.com","skills":["Python"]}'
        with patch('requests.post') as post:
            post.return_value = _make_response(sample_json)
            parsed = engine.parse_resume('dummy resume')
            self.assertEqual(parsed.get('name'), 'Alice')
            self.assertEqual(parsed.get('email'), 'alice@example.com')
            self.assertIn('Python', parsed.get('skills', []))

    def test_generate_questions_success(self):
        engine = OllamaEngine()
        resp_json = '{"technical": ["t1","t2","t3","t4","t5"], "behavioral": ["b1","b2","b3","b4","b5"]}'
        with patch('requests.post') as post:
            post.return_value = _make_response(resp_json)
            questions = engine.generate_questions('jd', 'role', ['skill1'])
            self.assertEqual(len(questions), 10)
            self.assertEqual(questions[0]['question_type'], 'technical')
            self.assertEqual(questions[-1]['question_type'], 'behavioral')

    def test_evaluate_answer_success(self):
        engine = OllamaEngine()
        resp_json = '{"score": 8, "feedback": "Good answer", "topics_to_cover": "topic1"}'
        with patch('requests.post') as post:
            post.return_value = _make_response(resp_json)
            out = engine.evaluate_answer('q','a','role')
            self.assertEqual(out['score'], 8)
            self.assertIn('Good answer', out['feedback'])

    def test_is_available_true(self):
        engine = OllamaEngine()
        with patch('requests.get') as get:
            get.return_value = Mock(status_code=200)
            self.assertTrue(engine.is_available())

    def test_is_available_false(self):
        engine = OllamaEngine()
        with patch('requests.get') as get:
            get.side_effect = Exception('no')
            self.assertFalse(engine.is_available())

