import { Card } from "@/ui/card";
import { CheckCircle, PlayCircle, Lock, FileQuestion } from "lucide-react";

interface PlayerSidebarProps {
  videos: any[];
  activeVideo: any;
  setActiveVideo: (video: any) => void;
}

export function PlayerSidebar({ videos, activeVideo, setActiveVideo }: PlayerSidebarProps) {
  return (
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
                : activeVideo?.id === video.id
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
                    activeVideo?.id === video.id
                      ? "text-foreground"
                      : "opacity-50"
                  }`}
                />
              ) : (
                <PlayCircle
                  className={`h-4 w-4 ${
                    activeVideo?.id === video.id
                      ? "text-foreground"
                      : "opacity-50"
                  }`}
                />
              )}
            </div>
            <span
              className={`text-sm leading-snug line-clamp-2 ${
                activeVideo?.id === video.id ? "font-medium" : ""
              }`}
            >
              {index + 1}. {video.title}
            </span>
          </button>
        ))}
      </div>
    </Card>
  );
}
