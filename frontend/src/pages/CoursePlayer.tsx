import { useState, useEffect, useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { CheckCircle, PlayCircle, ArrowLeft, Loader2 } from "lucide-react";
import API from "@/services/auth";
import { useAuth } from "@/context/AuthContext";
import { ThemeToggle } from "@/components/ThemeToggle";
import { AnimatedBackground } from "@/components/AnimatedBackground";
import { useYouTubePlayer } from "@/hooks/useYouTubePlayer";
import { useProctoring } from "@/hooks/useProctoring";
import { WebcamPermissionGate } from "@/components/WebcamPermissionGate";
import { AttentionOverlay } from "@/components/AttentionOverlay";

const YT_PLAYER_ID = "yt-proctored-player";

export default function CoursePlayer() {
  const { id } = useParams();
  const { token } = useAuth();

  const [videos, setVideos] = useState<any[]>([]);
  const [activeVideo, setActiveVideo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState(false);

  // Proctoring permission state
  const [webcamGranted, setWebcamGranted] = useState(false);
  const [proctoringEnabled, setProctoringEnabled] = useState(false);

  // YouTube Player
  const { isReady: playerReady, play, pause, loadVideo } = useYouTubePlayer({
    containerId: YT_PLAYER_ID,
    videoId: activeVideo?.yt_video_id || "",
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
          setActiveVideo(data[0]);
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
  useEffect(() => {
    if (activeVideo && playerReady) {
      loadVideo(activeVideo.yt_video_id);
    }
  }, [activeVideo?.id]);

  const handleMarkComplete = async () => {
    if (!activeVideo) return;
    setCompleting(true);
    try {
      await API.post(
        `/api/progress/complete-video/${activeVideo.id}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setVideos(
        videos.map((v) =>
          v.id === activeVideo.id ? { ...v, is_completed: true } : v
        )
      );
      setActiveVideo({ ...activeVideo, is_completed: true });
    } catch (err) {
      console.error("Failed to mark video as complete", err);
    } finally {
      setCompleting(false);
    }
  };

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
              {/* Permission Gate */}
              {showGate && (
                <WebcamPermissionGate
                  status={proctoring.status === "idle" ? "idle" : proctoring.status as "requesting" | "denied" | "error"}
                  errorMessage={proctoring.errorMessage}
                  onRequestPermission={handleRequestPermission}
                />
              )}

              {/* YouTube Player container */}
              <div
                id={YT_PLAYER_ID}
                className={`w-full h-full ${showGate ? "invisible" : ""}`}
              />

              {/* Attention Lost Overlay */}
              <AttentionOverlay visible={proctoring.attentionLost} />
            </div>

            {/* Info bar */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 py-4">
              <div className="space-y-2">
                <h2 className="text-xl font-semibold">{activeVideo.title}</h2>
                <Badge variant="secondary">+{activeVideo.xp_reward} XP</Badge>
              </div>
              <Button
                onClick={handleMarkComplete}
                disabled={activeVideo.is_completed || completing}
                variant={activeVideo.is_completed ? "outline" : "default"}
                className={
                  activeVideo.is_completed
                    ? "border-green-600/30 bg-green-500/10 text-green-700 dark:text-green-400 hover:bg-green-500/15 active:scale-95 transition-transform"
                    : "active:scale-95 transition-transform"
                }
              >
                {completing ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle
                    className={`mr-2 h-4 w-4 ${
                      activeVideo.is_completed
                        ? "text-green-600 dark:text-green-400"
                        : ""
                    }`}
                  />
                )}
                {activeVideo.is_completed ? "Completed" : "Mark as Complete"}
              </Button>
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
                  onClick={() => setActiveVideo(video)}
                  className={`w-full text-left px-3 py-2.5 rounded-md flex items-start gap-3 transition-colors ${
                    activeVideo.id === video.id
                      ? "bg-accent text-foreground"
                      : "text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                  }`}
                >
                  <div className="mt-0.5 shrink-0">
                    {video.is_completed ? (
                      <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
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
    </div>
  );
}