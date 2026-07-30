"""
Playlists Router Aggregator
"""
from fastapi import APIRouter
from .playlists_ingest import router as ingest_router
from .playlists_get import router as get_router
from .playlists_videos import router as videos_router
from .playlists_delete import router as delete_router

router = APIRouter(tags=["Playlists"])

router.include_router(ingest_router)
router.include_router(get_router)
router.include_router(videos_router)
router.include_router(delete_router)
