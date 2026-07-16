import { useEffect, useRef, useState, useCallback } from "react";

interface UseYouTubePlayerOptions {
  containerId: string;
  videoId: string;
  onReady?: () => void;
  onStateChange?: (state: number) => void;
}

interface UseYouTubePlayerReturn {
  isReady: boolean;
  play: () => void;
  pause: () => void;
  loadVideo: (videoId: string) => void;

  getCurrentTime: () => number;
  getDuration: () => number;
  seekTo: (seconds: number) => void;
}

// Track whether the API script is loading/loaded globally
let apiLoadPromise: Promise<void> | null = null;

function loadYouTubeAPI(): Promise<void> {
  if (apiLoadPromise) return apiLoadPromise;

  apiLoadPromise = new Promise<void>((resolve) => {
    // If already loaded
    if (window.YT && window.YT.Player) {
      resolve();
      return;
    }

    // Set the global callback
    const existingCallback = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      existingCallback?.();
      resolve();
    };

    // Inject the script
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.async = true;
    document.head.appendChild(script);
  });

  return apiLoadPromise;
}

export function useYouTubePlayer({
  containerId,
  videoId,
  onReady,
  onStateChange,
}: UseYouTubePlayerOptions): UseYouTubePlayerReturn {
  const playerRef = useRef<YT.Player | null>(null);
  const [isReady, setIsReady] = useState(false);
  const onReadyRef = useRef(onReady);
  const onStateChangeRef = useRef(onStateChange);

  // Keep callback refs fresh
  onReadyRef.current = onReady;
  onStateChangeRef.current = onStateChange;

  useEffect(() => {
    let destroyed = false;

    async function init() {
      await loadYouTubeAPI();
      if (destroyed) return;

      const el = document.getElementById(containerId);
      if (!el) return;

      playerRef.current = new window.YT.Player(containerId, {
        width: "100%",
        height: "100%",
        videoId,
        playerVars: {
          autoplay: 0,
          controls: 1,
          modestbranding: 1,
          rel: 0,
          fs: 1,
          iv_load_policy: 3,
          enablejsapi: 1,
          origin: window.location.origin,
        },
        events: {
          onReady: () => {
            if (!destroyed) {
              setIsReady(true);
              onReadyRef.current?.();
            }
          },
          onStateChange: (event: YT.OnStateChangeEvent) => {
            if (!destroyed) {
              onStateChangeRef.current?.(event.data);
            }
          },
        },
      });
    }

    init();

    return () => {
      destroyed = true;
      if (playerRef.current) {
        try {
          playerRef.current.destroy();
        } catch {
          // Player may already be destroyed
        }
        playerRef.current = null;
      }
      setIsReady(false);
    };
  }, [containerId, videoId]);

  const play = useCallback(() => {
    if (playerRef.current && isReady) {
      playerRef.current.playVideo();
    }
  }, [isReady]);

  const pause = useCallback(() => {
    if (playerRef.current && isReady) {
      playerRef.current.pauseVideo();
    }
  }, [isReady]);

  const loadVideo = useCallback(
    (newVideoId: string) => {
      if (playerRef.current && isReady) {
        playerRef.current.loadVideoById(newVideoId);
      }
    },
    [isReady]
  );

  const getCurrentTime = useCallback(() => {
    if (playerRef.current && isReady) {
      return playerRef.current.getCurrentTime();
    }
    return 0;
  }, [isReady]);

  const getDuration = useCallback(() => {
    if (playerRef.current && isReady) {
      return playerRef.current.getDuration();
    }
    return 0;
  }, [isReady]);

  const seekTo = useCallback(
    (seconds: number) => {
      if (playerRef.current && isReady) {
        playerRef.current.seekTo(seconds, true);
      }
    },
    [isReady]
  );

  return {
  isReady,
  play,
  pause,
  loadVideo,
  getCurrentTime,
  getDuration,
  seekTo,
};
}
