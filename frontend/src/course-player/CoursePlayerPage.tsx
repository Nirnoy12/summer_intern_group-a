import { Link } from "react-router-dom";
import { Button } from "@/ui/button";
import { ArrowLeft, Loader2 } from "lucide-react";
import { QuizView } from "./quiz/QuizView";
import { PlayerSidebar } from "./PlayerSidebar";
import { PlayerControls } from "./PlayerControls";
import { ThemeToggle } from "@/theme/ThemeToggle";
import { AnimatedBackground } from "@/theme/AnimatedBackground";
import { WebcamPermissionGate } from "@/course-player/WebcamPermissionGate";
import { AttentionOverlay } from "@/course-player/AttentionOverlay";
import { CameraPip } from "@/course-player/CameraPip";
import { useCoursePlayer } from "./useCoursePlayer";

export default function CoursePlayer() {
  const { videos, setVideos, activeVideo, setActiveVideo, loading, webcamGranted, proctoring, handleRequestPermission, YT_PLAYER_ID } = useCoursePlayer();

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-background text-foreground"><Loader2 className="w-8 h-8 text-primary animate-spin" /></div>;

  if (!webcamGranted) {
    return (
      <div className="min-h-screen text-foreground transition-colors duration-300 relative">
        <AnimatedBackground />
        <div className="max-w-7xl mx-auto p-4 sm:p-6 space-y-4 relative z-10">
          <div className="flex items-center justify-between">
            <Link to="/dashboard"><Button variant="ghost" size="sm"><ArrowLeft className="mr-2 h-4 w-4" />Back to Dashboard</Button></Link>
            <ThemeToggle />
          </div>
          <WebcamPermissionGate status={proctoring.status} errorMessage={proctoring.errorMessage} onRequestPermission={handleRequestPermission} />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen text-foreground transition-colors duration-300 relative">
      <AnimatedBackground />
      <AttentionOverlay visible={proctoring.attentionLost} />
      <div className="max-w-[1600px] mx-auto p-4 sm:p-6 flex flex-col h-screen relative z-10">
        <div className="flex items-center justify-between pb-4 shrink-0">
          <Link to="/dashboard"><Button variant="ghost" size="sm"><ArrowLeft className="mr-2 h-4 w-4" />Back to Dashboard</Button></Link>
          <ThemeToggle />
        </div>
        <div className="flex flex-col lg:flex-row gap-4 flex-1 min-h-0">
          <div className="flex-1 flex flex-col gap-4">
            <div className="aspect-video w-full bg-black rounded-lg overflow-hidden border border-border relative">
              {activeVideo?.type === "quiz" ? (
                <QuizView
                  quiz={activeVideo}
                  onPassed={() => {
                    setVideos((prev) => prev.map((v) => v.id === activeVideo.id ? { ...v, is_completed: true } : v));
                    setActiveVideo((prev: any) => ({ ...prev, is_completed: true }));
                  }}
                  onSkip={() => {
                    setVideos((prev) => {
                      const currentIndex = prev.findIndex((v) => v.id === activeVideo.id);
                      const nextVideo = prev[currentIndex + 1];
                      if (nextVideo && !nextVideo.is_locked) setActiveVideo(nextVideo);
                      return prev;
                    });
                  }}
                />
              ) : (
                <div id={YT_PLAYER_ID} className="w-full h-full" />
              )}
            </div>
            <PlayerControls activeVideo={activeVideo} videos={videos} setActiveVideo={setActiveVideo} />
          </div>
          <PlayerSidebar videos={videos} activeVideo={activeVideo} setActiveVideo={setActiveVideo} />
        </div>
      </div>
      <CameraPip stream={proctoring.stream} />
    </div>
  );
}