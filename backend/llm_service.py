import asyncio
import json
import logging
from typing import List
from uuid import UUID
from sqlmodel import Session, select
import httpx

from youtube_transcript_api import YouTubeTranscriptApi
from models import Quiz, Question, Video

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with the actual model you are using in Ollama, e.g., 'phi3' or 'llama3'
OLLAMA_MODEL = "phi3"
OLLAMA_URL = "http://localhost:11434/api/generate"


def get_transcripts_for_videos(video_ids: List[str]) -> str:
    """Fetches and concatenates transcripts for a list of YouTube video IDs."""
    combined_transcript = ""
    for v_id in video_ids:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(v_id)
            text = " ".join([t['text'] for t in transcript])
            combined_transcript += f"Video {v_id} Transcript:\n{text}\n\n"
        except Exception as e:
            logger.error(f"Could not fetch transcript for {v_id}: {e}")
            combined_transcript += f"Video {v_id} Transcript: [Unavailable]\n\n"
    return combined_transcript


async def generate_questions_with_ollama(transcript_text: str, num_questions: int = 10) -> List[dict]:
    """Uses Ollama to generate multiple choice questions based on the transcript."""
    prompt = f"""
You are an expert educator. Based on the following video transcripts, generate {num_questions} in-depth multiple-choice questions to test a student's understanding.

Output ONLY a JSON array of objects, with no markdown formatting or extra text. The structure of each object must be exactly:
{{
    "question_text": "The question here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_option_index": 0,
    "explanation": "Brief explanation of why this is correct."
}}

Transcripts:
{transcript_text[:12000]}  # Limiting length to fit within context window comfortably
"""
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "[]")
            
            try:
                questions = json.loads(response_text)
                if isinstance(questions, dict):
                    # Sometimes LLMs wrap it in a dict with a key
                    for key in questions:
                        if isinstance(questions[key], list):
                            return questions[key]
                if isinstance(questions, list):
                    return questions
                return []
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from LLM: {response_text}")
                return []
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return []


async def generate_quiz_pool_background(quiz_id: UUID, video_yt_ids: List[str], engine):
    """Background task to generate a pool of questions for a quiz."""
    logger.info(f"Starting background generation for Quiz {quiz_id}")
    
    # 1. Fetch transcripts
    transcripts = get_transcripts_for_videos(video_yt_ids)
    
    if not transcripts.strip():
        logger.warning(f"No transcripts found for Quiz {quiz_id}. Skipping generation.")
        with Session(engine) as session:
            quiz = session.get(Quiz, quiz_id)
            if quiz:
                quiz.status = "error_no_transcript"
                session.commit()
        return

    # 2. Generate multiple batches of questions to build a pool
    # The user requested 30 questions per attempt, so we should generate at least 60-90.
    # To keep the LLM request manageable, we'll request 15 at a time, 4 times.
    all_questions = []
    
    for i in range(4): # Generate 60 questions total (4 batches of 15)
        logger.info(f"Generating batch {i+1} for Quiz {quiz_id}")
        questions = await generate_questions_with_ollama(transcripts, num_questions=15)
        if questions:
            all_questions.extend(questions)
    
    if not all_questions:
        logger.error(f"Failed to generate any questions for Quiz {quiz_id}")
        with Session(engine) as session:
            quiz = session.get(Quiz, quiz_id)
            if quiz:
                quiz.status = "error_llm_failure"
                session.commit()
        return

    # 3. Save to database
    with Session(engine) as session:
        for q_data in all_questions:
            # Validate structure
            if 'question_text' in q_data and 'options' in q_data and 'correct_option_index' in q_data:
                question = Question(
                    quiz_id=quiz_id,
                    question_text=q_data['question_text'],
                    options={"choices": q_data['options']}, # Storing inside a dict for JSON column
                    correct_option_index=int(q_data['correct_option_index']),
                    explanation=q_data.get('explanation', '')
                )
                session.add(question)
        
        quiz = session.get(Quiz, quiz_id)
        if quiz:
            quiz.status = "ready"
        session.commit()
        
    logger.info(f"Successfully generated {len(all_questions)} questions for Quiz {quiz_id}")
