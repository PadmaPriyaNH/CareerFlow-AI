from unittest.mock import patch, Mock
from interviews.services.ollama_engine import OllamaEngine


def make_response(text, status=200):
    m = Mock()
    m.status_code = status
    m.json.return_value = {"response": text}
    m.raise_for_status = Mock()
    return m


def test_parse_resume_success():
    engine = OllamaEngine()
    sample_json = '{"name":"Alice","email":"alice@example.com","skills":["Python"]}'
    with patch('requests.post') as post:
        post.return_value = make_response(sample_json)
        parsed = engine.parse_resume('dummy resume')
        assert parsed.get('name') == 'Alice'
        assert parsed.get('email') == 'alice@example.com'
        assert 'Python' in parsed.get('skills', [])


def test_generate_questions_success():
    engine = OllamaEngine()
    resp_json = '{"technical": ["t1","t2","t3","t4","t5"], "behavioral": ["b1","b2","b3","b4","b5"]}'
    with patch('requests.post') as post:
        post.return_value = make_response(resp_json)
        questions = engine.generate_questions('jd', 'role', ['skill1'])
        assert len(questions) == 10
        assert questions[0]['question_type'] == 'technical'
        assert questions[-1]['question_type'] == 'behavioral'


def test_evaluate_answer_success():
    engine = OllamaEngine()
    resp_json = '{"score": 8, "feedback": "Good answer", "topics_to_cover": "topic1"}'
    with patch('requests.post') as post:
        post.return_value = make_response(resp_json)
        out = engine.evaluate_answer('q','a','role')
        assert out['score'] == 8
        assert 'Good answer' in out['feedback']


def test_is_available_true():
    engine = OllamaEngine()
    with patch('requests.get') as get:
        get.return_value = Mock(status_code=200)
        assert engine.is_available() is True


def test_is_available_false():
    engine = OllamaEngine()
    with patch('requests.get') as get:
        get.side_effect = Exception('no')
        assert engine.is_available() is False
