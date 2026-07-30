import { Button } from "@/ui/button";
import { Badge } from "@/ui/badge";

interface PlayerControlsProps {
  activeVideo: any;
  videos: any[];
  setActiveVideo: (video: any) => void;
}

export function PlayerControls({ activeVideo, videos, setActiveVideo }: PlayerControlsProps) {
  if (!activeVideo) return null;

  return (
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
            (() => {
              const idx = videos.findIndex((v) => v.id === activeVideo.id);
              if (idx >= videos.length - 1) return true;
              const next = videos[idx + 1];
              // If next item is a quiz, check the item after it (quizzes are optional)
              if (next?.type === "quiz") {
                const afterQuiz = videos[idx + 2];
                return afterQuiz ? afterQuiz.is_locked : false;
              }
              return next?.is_locked ?? false;
            })()
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
  );
}
