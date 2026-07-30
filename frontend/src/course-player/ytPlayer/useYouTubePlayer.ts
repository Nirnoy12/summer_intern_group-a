import { useEffect, useRef, useState, useCallback } from "react";
import type { UseYouTubePlayerOptions, UseYouTubePlayerReturn } from "./types";
import { loadYouTubeAPI } from "./loadYouTubeAPI";

export function useYouTubePlayer({ containerId, videoId, onReady, onStateChange }: UseYouTubePlayerOptions): UseYouTubePlayerReturn {
  const playerRef = useRef<YT.Player | null>(null);
  const [isReady, setIsReady] = useState(false);
  const onReadyRef = useRef(onReady);
  const onStateChangeRef = useRef(onStateChange);

  onReadyRef.current = onReady;
  onStateChangeRef.current = onStateChange;

  useEffect(() => {
    let destroyed = false;

    async function init() {
      await loadYouTubeAPI();
      if (destroyed) return;
      const el = document.getElementById(containerId);
      if (!el || !videoId) return;

      playerRef.current = new window.YT.Player(containerId, {
        width: "100%", height: "100%", videoId,
        playerVars: { autoplay: 0, controls: 1, modestbranding: 1, rel: 0, fs: 1, iv_load_policy: 3, enablejsapi: 1, origin: window.location.origin },
        events: {
          onReady: () => { if (!destroyed) { setIsReady(true); onReadyRef.current?.(); } },
          onStateChange: (event: YT.OnStateChangeEvent) => { if (!destroyed) { onStateChangeRef.current?.(event.data); } },
        },
      });
    }

    init();

    return () => {
      destroyed = true;
      if (playerRef.current) {
        try { playerRef.current.destroy(); } catch {}
        playerRef.current = null;
      }
      setIsReady(false);
    };
  }, [containerId, videoId]);

  const play = useCallback(() => { if (playerRef.current && isReady) playerRef.current.playVideo(); }, [isReady]);
  const pause = useCallback(() => { if (playerRef.current && isReady) playerRef.current.pauseVideo(); }, [isReady]);
  const loadVideo = useCallback((newVideoId: string) => { if (playerRef.current && isReady) playerRef.current.loadVideoById(newVideoId); }, [isReady]);
  const getCurrentTime = useCallback(() => (playerRef.current && isReady ? playerRef.current.getCurrentTime() : 0), [isReady]);
  const getDuration = useCallback(() => (playerRef.current && isReady ? playerRef.current.getDuration() : 0), [isReady]);
  const seekTo = useCallback((seconds: number) => { if (playerRef.current && isReady) playerRef.current.seekTo(seconds, true); }, [isReady]);

  return { isReady, play, pause, loadVideo, getCurrentTime, getDuration, seekTo };
}
