import { useState, useEffect, useCallback, useRef } from "react";
import { useParams } from "react-router-dom";
import API from "@/auth/auth";
import { useAuth } from "@/auth/AuthContext";
import { useYouTubePlayer } from "@/course-player/ytPlayer/useYouTubePlayer";
import { useProctoring } from "@/course-player/proctoring/useProctoring";

const YT_PLAYER_ID = "yt-proctored-player";

export function useCoursePlayer() {
  const { id } = useParams();
  const { token } = useAuth();

  const [videos, setVideos] = useState<any[]>([]);
  const [activeVideo, setActiveVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [webcamGranted, setWebcamGranted] = useState(false);
  const [proctoringEnabled, setProctoringEnabled] = useState(false);

  const isSendingRef = useRef(false);
  const pendingSeekRef = useRef<number | null>(null);
  const maxWatchedRef = useRef(0);

  const { isReady: playerReady, play, pause, loadVideo, getCurrentTime, getDuration, seekTo } = useYouTubePlayer({
    containerId: YT_PLAYER_ID,
    videoId: activeVideo?.yt_video_id || "",
    onStateChange: (state) => { setIsPlaying(state === YT.PlayerState.PLAYING); },
  });

  const handleAttentionLost = useCallback(() => { pause(); }, [pause]);
  const handleAttentionRegained = useCallback(() => { play(); }, [play]);

  const proctoring = useProctoring({
    enabled: proctoringEnabled,
    lookAwayThresholdMs: 3000,
    onAttentionLost: handleAttentionLost,
    onAttentionRegained: handleAttentionRegained,
  });

  useEffect(() => {
    if (proctoring.status === "active") setWebcamGranted(true);
  }, [proctoring.status]);

  const handleRequestPermission = useCallback(() => { setProctoringEnabled(true); }, []);

  useEffect(() => {
    async function fetchVideos() {
      try {
        const res = await API.get(`/api/playlists/${id}/videos`, { headers: { Authorization: `Bearer ${token}` } });
        setVideos(res.data);
        if (res.data.length > 0) {
          const firstPlayable = res.data.find((v: any) => !v.is_locked && !v.is_completed) || res.data[0];
          setActiveVideo(firstPlayable);
        }
      } catch (err) {
        console.error("Failed to fetch videos", err);
      } finally {
        setLoading(false);
      }
    }
    if (id) fetchVideos();
  }, [id, token]);

  useEffect(() => {
    if (activeVideo && activeVideo.type !== "quiz" && playerReady) {
      pendingSeekRef.current = activeVideo.last_watched_second > 0 ? activeVideo.last_watched_second : null;
      loadVideo(activeVideo.yt_video_id);
    }
  }, [activeVideo?.id, playerReady, loadVideo]);

  useEffect(() => {
    if (isPlaying && pendingSeekRef.current !== null) {
      seekTo(pendingSeekRef.current);
      pendingSeekRef.current = null;
    }
  }, [isPlaying, seekTo]);

  useEffect(() => {
    if (activeVideo) maxWatchedRef.current = activeVideo.highest_watched_second || 0;
  }, [activeVideo?.id]);

  useEffect(() => {
    if (!playerReady || !isPlaying) return;
    const skipInterval = setInterval(() => {
      const current = getCurrentTime();
      if (current > maxWatchedRef.current + 2.5) {
        seekTo(maxWatchedRef.current);
      } else {
        maxWatchedRef.current = Math.max(maxWatchedRef.current, current);
      }
    }, 1000);
    return () => clearInterval(skipInterval);
  }, [playerReady, isPlaying, getCurrentTime, seekTo]);

  useEffect(() => {
    if (!playerReady || !activeVideo || activeVideo.type === "quiz") return;
    const interval = setInterval(async () => {
      if (!isPlaying || isSendingRef.current) return;
      const currentTime = getCurrentTime();
      const duration = getDuration();
      if (duration <= 0) return;

      isSendingRef.current = true;
      try {
        const res = await API.post("/api/progress/update", { video_id: activeVideo.id, current_time: currentTime, duration: duration }, { headers: { Authorization: `Bearer ${token}` } });
        const data = res.data;
        if (!data.allowed) { seekTo(data.seek_to); return; }

        setVideos((prev) => {
          const updated = prev.map((v) => v.id === activeVideo.id ? { ...v, is_completed: data.completed, highest_watched_second: data.highest_watched_second, last_watched_second: data.last_watched_second } : v);
          let prevCompleted = true;
          return updated.map((v) => {
            const isLocked = !prevCompleted;
            if (v.type !== "quiz") prevCompleted = v.is_completed;
            return { ...v, is_locked: isLocked };
          });
        });

        setActiveVideo((prev: any) => prev ? { ...prev, is_completed: data.completed, highest_watched_second: data.highest_watched_second, last_watched_second: data.last_watched_second } : prev);

        if (data.completed && !activeVideo.is_completed) {
          setVideos((prev) => {
            const currentIndex = prev.findIndex((v) => v.id === activeVideo.id);
            let nextIdx = currentIndex + 1;
            if (nextIdx < prev.length && prev[nextIdx].type === "quiz") nextIdx += 1;
            const nextVideo = prev[nextIdx];
            if (nextVideo && !nextVideo.is_completed) setActiveVideo({ ...nextVideo, is_locked: false });
            return prev;
          });
        }
      } catch (err) {
        console.error("Failed to update progress", err);
      } finally {
        isSendingRef.current = false;
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [playerReady, isPlaying, activeVideo, token, getCurrentTime, getDuration, seekTo]);

  return {
    videos, setVideos, activeVideo, setActiveVideo, loading, webcamGranted, proctoring, handleRequestPermission, YT_PLAYER_ID
  };
}
