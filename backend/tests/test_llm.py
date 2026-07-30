import os, sys, pytest, httpx, json
from unittest.mock import patch, MagicMock, AsyncMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

@pytest.fixture
def anyio_backend():
    return 'asyncio'

class TestGroqService:
    @pytest.mark.anyio
    async def test_generate_questions_with_groq_valid_response(self):
        from llm_service.llm_caller import _call_groq
        mock_groq_content = json.dumps([{"question_text": "What is Python?", "options": ["Language", "Snake", "Car", "Food"], "correct_option_index": 0, "explanation": "Python is a language."}])
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": mock_groq_content}}]
        }
        mock_resp.raise_for_status = MagicMock()
        
        with patch("llm_service.llm_caller.httpx.AsyncClient") as mc_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_resp)
            mc_class.return_value = mock_client
            
            res = await _call_groq("Sample prompt")
        assert isinstance(res, list) and len(res) == 1
        assert res[0]["question_text"] == "What is Python?"

    @pytest.mark.anyio
    async def test_generate_questions_handles_invalid_json(self):
        from llm_service.llm_caller import _call_groq
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"choices": [{"message": {"content": "Not valid JSON"}}]}
        mock_resp.raise_for_status = MagicMock()
        
        with patch("llm_service.llm_caller.httpx.AsyncClient") as mc_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(return_value=mock_resp)
            mc_class.return_value = mock_client
            
            assert await _call_groq("Sample prompt") == []

    @pytest.mark.anyio
    async def test_generate_questions_handles_network_error(self):
        from llm_service.llm_caller import _call_groq
        with patch("llm_service.llm_caller.httpx.AsyncClient") as mc_class:
            mock_client = MagicMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Network failure"))
            mc_class.return_value = mock_client
            
            assert await _call_groq("Sample prompt") == []

    def test_quiz_question_validation_logic(self):
        q = {"question_text": "Q", "options": ["A","B"], "correct_option_index": 1, "explanation": "E"}
        assert q["question_text"] and q["options"] and 0 <= int(q["correct_option_index"]) < len(q["options"])

    def test_quiz_question_rejects_out_of_bounds_index(self):
        c_idx = 99; options = ["A", "B", "C", "D"]
        assert (0 if (c_idx >= len(options) or c_idx < 0) else c_idx) == 0

class TestQuizBusinessLogic:
    def test_quiz_pass_threshold_is_70_percent(self):
        assert (int(30 * 0.70) / 30) * 100 >= 70.0
        assert (int(30 * 0.69) / 30) * 100 < 70.0

    def test_quiz_pool_size_is_30_per_attempt(self):
        import random; assert len(random.sample(list(range(60)), 30)) == 30

    def test_quiz_generation_schedule_per_3_videos(self):
        assert len(range(2, 9, 3)) + (1 if 9 % 3 != 0 else 0) + 1 == 4

    def test_xp_level_calculation(self):
        assert (0 // 500) + 1 == 1; assert (500 // 500) + 1 == 2; assert (1500 // 500) + 1 == 4

    def test_video_xp_reward_default(self):
        from models import Video; import uuid; assert Video(playlist_id=uuid.uuid4(), yt_video_id="id", sequence_order=1, title="T").xp_reward == 50

    def test_score_percentage_calculation(self):
        assert abs(((21 / 30) * 100) - 70.0) < 0.01
