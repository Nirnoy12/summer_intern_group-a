import { useState, useEffect, useCallback, useRef } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/ui/button";
import { Badge } from "@/ui/badge";
import { Card } from "@/ui/card";
import { CheckCircle, PlayCircle, ArrowLeft, Loader2, Lock, FileQuestion } from "lucide-react";
import { QuizView } from "./QuizView";
import API from "@/auth/auth";
import { useAuth } from "@/auth/AuthContext";
import { ThemeToggle } from "@/theme/ThemeToggle";
import { AnimatedBackground } from "@/theme/AnimatedBackground";
import { useYouTubePlayer } from "@/course-player/useYouTubePlayer";
import { useProctoring } from "@/course-player/useProctoring";
import { WebcamPermissionGate } from "@/course-player/WebcamPermissionGate";
import { AttentionOverlay } from "@/course-player/AttentionOverlay";
import { CameraPip } from "@/course-player/CameraPip";

const YT_PLAYER_ID = "yt-proctored-player";

export default function CoursePlayer() {
  const { id } = useParams();
  const { token } = useAuth();

  const [videos, setVideos] = useState<any[]>([]);
  const [activeVideo, setActiveVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  // Proctoring permission state
  const [webcamGranted, setWebcamGranted] = useState(false);
  const [proctoringEnabled, setProctoringEnabled] = useState(false);

  // Ref to guard against overlapping progress API calls
  const isSendingRef = useRef(false);

  // YouTube Player
  const {
    isReady: playerReady,
    play,
    pause,
    loadVideo,
    getCurrentTime,
    getDuration,
    seekTo,
  } = useYouTubePlayer({
    containerId: YT_PLAYER_ID,
    videoId: activeVideo?.yt_video_id || "",
    onStateChange: (state) => {
      setIsPlaying(state === YT.PlayerState.PLAYING);
    },
  });

  // Proctoring callbacks
  const handleAttentionLost = useCallback(() => {
    pause();
  }, [pause]);

  const handleAttentionRegained = useCallback(() => {
    play();
  }, [play]);

  // Proctoring hook
  const proctoring = useProctoring({
    enabled: proctoringEnabled,
    lookAwayThresholdMs: 3000,
    onAttentionLost: handleAttentionLost,
    onAttentionRegained: handleAttentionRegained,
  });

  // When proctoring status changes to active, mark webcam as granted
  useEffect(() => {
    if (proctoring.status === "active") {
      setWebcamGranted(true);
    }
  }, [proctoring.status]);

  // Request permission handler
  const handleRequestPermission = useCallback(() => {
    setProctoringEnabled(true);
  }, []);

  // Fetch videos
  useEffect(() => {
    async function fetchVideos() {
      try {
        const res = await API.get(`/api/playlists/${id}/videos`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = res.data;
        setVideos(data);
        if (data.length > 0) {
          // Select the first unlocked, incomplete video (or first video as fallback)
          const firstPlayable = data.find(
            (v: any) => !v.is_locked && !v.is_completed
          ) || data[0];
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

  // When active video changes, load the new video into the player
  const pendingSeekRef = useRef<number | null>(null);

  useEffect(() => {
    if (activeVideo && activeVideo.type !== "quiz" && playerReady) {
      // Store the seek position so the onStateChange handler can seek after loading
      if (activeVideo.last_watched_second > 0) {
        pendingSeekRef.current = activeVideo.last_watched_second;
      } else {
        pendingSeekRef.current = null;
      }
      loadVideo(activeVideo.yt_video_id);
    }
  }, [activeVideo?.id, playerReady, loadVideo]);

  // Seek to saved position once the player starts buffering/playing the new video
  useEffect(() => {
    if (isPlaying && pendingSeekRef.current !== null) {
      seekTo(pendingSeekRef.current);
      pendingSeekRef.current = null;
    }
  }, [isPlaying, seekTo]);

  // Strict Frontend Anti-Skip
  const maxWatchedRef = useRef(0);

  useEffect(() => {
    if (activeVideo) {
      maxWatchedRef.current = activeVideo.highest_watched_second || 0;
    }
  }, [activeVideo?.id]);

  useEffect(() => {
    if (!playerReady || !isPlaying) return;

    const skipInterval = setInterval(() => {
      const current = getCurrentTime();
      // If user skipped ahead more than 2.5 seconds from what they watched, bounce them back
      if (current > maxWatchedRef.current + 2.5) {
        seekTo(maxWatchedRef.current);
      } else {
        maxWatchedRef.current = Math.max(maxWatchedRef.current, current);
      }
    }, 1000);

    return () => clearInterval(skipInterval);
  }, [playerReady, isPlaying, getCurrentTime, seekTo]);

  // Progress polling — every 5s to reduce server load, with overlap guard
  useEffect(() => {
    if (!playerReady || !activeVideo || activeVideo.type === "quiz") return;

    const interval = setInterval(async () => {
      // Skip if not playing, or if a previous request is still in-flight
      if (!isPlaying || isSendingRef.current) return;

      const currentTime = getCurrentTime();
      const duration = getDuration();
      if (duration <= 0) return;

      isSendingRef.current = true;
      try {
        const res = await API.post(
          "/api/progress/update",
          {
            video_id: activeVideo.id,
            current_time: currentTime,
            duration: duration,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        const data = res.data;

        if (!data.allowed) {
          seekTo(data.seek_to);
          return;
        }

        // Update video list with latest progress
        setVideos((prev) => {
          const updated = prev.map((video) =>
            video.id === activeVideo.id
              ? {
                  ...video,
                  is_completed: data.completed,
                  highest_watched_second: data.highest_watched_second,
                  last_watched_second: data.last_watched_second,
                }
              : video
          );

          // Recalculate is_locked for all videos after progress update
          let prevCompleted = true;
          return updated.map((video) => {
            const isLocked = !prevCompleted;
            prevCompleted = video.is_completed;
            return { ...video, is_locked: isLocked };
          });
        });

        setActiveVideo((prev: any) =>
          prev
            ? {
                ...prev,
                is_completed: data.completed,
                highest_watched_second: data.highest_watched_second,
                last_watched_second: data.last_watched_second,
              }
            : prev
        );

        // Auto-advance: if current video just completed, move to the next one
        if (data.completed && !activeVideo.is_completed) {
          setVideos((prev) => {
            const currentIndex = prev.findIndex((v) => v.id === activeVideo.id);
            const nextVideo = prev[currentIndex + 1];
            if (nextVideo && !nextVideo.is_completed) {
              setActiveVideo({ ...nextVideo, is_locked: false });
            }
            return prev;
          });
        }
      } catch (err) {
        console.error("Progress update failed:", err);
      } finally {
        isSendingRef.current = false;
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [playerReady, activeVideo, token, getCurrentTime, getDuration, seekTo, isPlaying]);

  // Tab visibility tracker: Enforce active tab
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        pause();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [pause]);


  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-muted-foreground animate-spin" />
      </div>
    );
  }

  if (!videos.length || !activeVideo) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-4 text-muted-foreground">
        <p className="text-lg">No videos found for this playlist.</p>
        <Link to="/dashboard">
          <Button variant="outline">Return to Dashboard</Button>
        </Link>
      </div>
    );
  }

  // Show permission gate if webcam not yet granted
  const showGate =
    !webcamGranted &&
    (proctoring.status === "idle" ||
      proctoring.status === "requesting" ||
      proctoring.status === "denied" ||
      proctoring.status === "error");

  // Determine tracking indicator color
  const getIndicatorClass = () => {
    if (proctoring.status !== "active") return "";
    if (!proctoring.isFaceDetected) return "tracking-indicator--amber";
    if (proctoring.isLookingAway) return "tracking-indicator--amber";
    return "tracking-indicator--green";
  };

  return (
    <div className="min-h-screen text-foreground relative">
      <AnimatedBackground />
      <div className="max-w-7xl mx-auto px-4 py-6 md:px-6 flex flex-col h-screen relative z-10">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-4">
          <Link to="/dashboard">
            <Button
              variant="ghost"
              className="-ml-2 active:scale-95 transition-transform"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
          <div className="flex items-center gap-3">
            {/* Tracking indicator dot */}
            {proctoring.status === "active" && (
              <div
                className={`tracking-indicator ${getIndicatorClass()}`}
                title={
                  proctoring.isFaceDetected
                    ? proctoring.isLookingAway
                      ? "Looking away"
                      : "Tracking active"
                    : "No face detected"
                }
              />
            )}
            <ThemeToggle />
          </div>
        </div>

        {/* Two-column layout */}
        <div className="flex flex-col lg:flex-row gap-4 flex-1 min-h-0">
          {/* Left: Video player and info */}
          <div className="flex-1 flex flex-col gap-4">
            {/* Video player area */}
            <div className="aspect-video w-full bg-black rounded-lg overflow-hidden border border-border relative">
              {activeVideo?.type === "quiz" ? (
                <QuizView 
                  quiz={activeVideo} 
                  onPassed={() => {
                    // Update the active video status to completed
                    setVideos((prev) => {
                      const updated = prev.map((video) =>
                        video.id === activeVideo.id
                          ? { ...video, is_completed: true }
                          : video
                      );
                      
                      let prevCompleted = true;
                      return updated.map((video) => {
                        const isLocked = !prevCompleted;
                        prevCompleted = video.is_completed;
                        return { ...video, is_locked: isLocked };
                      });
                    });
                    
                    setActiveVideo((prev: any) => ({...prev, is_completed: true}));
                  }} 
                />
              ) : (
                <>
                  {/* Permission Gate */}
                  {showGate && (
                    <WebcamPermissionGate
                      status={proctoring.status === "idle" ? "idle" : proctoring.status as "requesting" | "denied" | "error"}
                      errorMessage={proctoring.errorMessage}
                      onRequestPermission={handleRequestPermission}
                    />
                  )}

                  {/* YouTube Player container */}
                  <div className={`w-full h-full ${showGate ? "invisible" : ""}`}>
                    <div id={YT_PLAYER_ID} className="w-full h-full" />
                  </div>

                  {/* Attention Lost Overlay */}
                  <AttentionOverlay visible={proctoring.attentionLost} />
                </>
              )}
            </div>

            {/* Info bar */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 py-4">
              <div className="space-y-2">
                <h2 className="text-xl font-semibold">{activeVideo.title}</h2>
                {activeVideo.type !== "quiz" && (
                  <Badge variant="secondary">+{activeVideo.xp_reward} XP</Badge>
                )}
              </div>
              
              {/* Navigation buttons */}
              <div className="flex gap-2">
                <Button 
                  variant="outline"
                  disabled={videos.findIndex((v) => v.id === activeVideo.id) === 0}
                  onClick={() => {
                    const idx = videos.findIndex((v) => v.id === activeVideo.id);
                    if (idx > 0) setActiveVideo(videos[idx - 1]);
                  }}
                >
                  Previous
                </Button>
                <Button 
                  variant="default"
                  disabled={
                    videos.findIndex((v) => v.id === activeVideo.id) >= videos.length - 1 || 
                    videos[videos.findIndex((v) => v.id === activeVideo.id) + 1].is_locked
                  }
                  onClick={() => {
                    const idx = videos.findIndex((v) => v.id === activeVideo.id);
                    if (idx < videos.length - 1) setActiveVideo(videos[idx + 1]);
                  }}
                >
                  Next
                </Button>
              </div>
            </div>
          </div>

          {/* Right sidebar */}
          <Card className="w-full lg:w-80 flex flex-col overflow-hidden glass-card">
            <div className="p-4 border-b border-border">
              <h3 className="text-base font-semibold">Course Videos</h3>
              <p className="text-xs text-muted-foreground mt-1">
                {videos.length} {videos.length === 1 ? "video" : "videos"}
              </p>
            </div>
            <div className="overflow-y-auto flex-1 p-2 space-y-1">
              {videos.map((video, index) => (
                <button
                  key={video.id}
                  onClick={() => {
                    if (!video.is_locked) setActiveVideo(video);
                  }}
                  disabled={video.is_locked}
                  className={`w-full text-left px-3 py-2.5 rounded-md flex items-start gap-3 transition-colors ${
                    video.is_locked
                      ? "opacity-40 cursor-not-allowed"
                      : activeVideo.id === video.id
                        ? "bg-accent text-foreground"
                        : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                  }`}
                >
                  <div className="mt-0.5 shrink-0">
                    {video.is_locked ? (
                      <Lock className="h-4 w-4 text-muted-foreground" />
                    ) : video.is_completed ? (
                      <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                    ) : video.type === "quiz" ? (
                      <FileQuestion
                        className={`h-4 w-4 ${
                          activeVideo.id === video.id
                            ? "text-foreground"
                            : "opacity-50"
                        }`}
                      />
                    ) : (
                      <PlayCircle
                        className={`h-4 w-4 ${
                          activeVideo.id === video.id
                            ? "text-foreground"
                            : "opacity-50"
                        }`}
                      />
                    )}
                  </div>
                  <span
                    className={`text-sm leading-snug line-clamp-2 ${
                      activeVideo.id === video.id ? "font-medium" : ""
                    }`}
                  >
                    {index + 1}. {video.title}
                  </span>
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
      <CameraPip stream={proctoring.stream} />
    </div>
  );
}