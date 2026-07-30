import asyncio
import itertools
import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)

PRIORITY_URGENT   = 0
PRIORITY_FIRST    = 10
PRIORITY_CHAIN    = 20
PRIORITY_RECOVERY = 30

_job_counter = itertools.count()

@dataclass(order=True)
class QuizJob:
    priority: int
    seq:           int               
    shared_quiz_id: UUID             = field(compare=False)
    video_yt_ids:   list[str]        = field(compare=False)
    questions_per_attempt: int       = field(compare=False)
    engine:         Any              = field(compare=False)

_quiz_queue:          asyncio.PriorityQueue = asyncio.PriorityQueue()
_queued_or_running:   set[UUID]             = set()

def enqueue_quiz(
    shared_quiz_id: UUID,
    video_yt_ids: list[str],
    questions_per_attempt: int,
    engine: Any,
    priority: int = PRIORITY_CHAIN,
) -> bool:
    if shared_quiz_id in _queued_or_running and priority != PRIORITY_URGENT:
        return False

    job = QuizJob(
        priority=priority,
        seq=next(_job_counter),
        shared_quiz_id=shared_quiz_id,
        video_yt_ids=video_yt_ids,
        questions_per_attempt=questions_per_attempt,
        engine=engine,
    )
    _queued_or_running.add(shared_quiz_id)
    _quiz_queue.put_nowait(job)
    return True
