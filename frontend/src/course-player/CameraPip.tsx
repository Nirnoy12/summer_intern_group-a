import { useEffect, useRef } from "react";
import { Maximize2, Minimize2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/ui/button";

interface CameraPipProps {
  stream: MediaStream | null;
}

export function CameraPip({ stream }: CameraPipProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  if (!stream) return null;

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 overflow-hidden rounded-xl border-2 border-primary/20 bg-black shadow-2xl transition-all duration-300 ${
        expanded ? "h-64 w-80" : "h-32 w-48"
      }`}
    >
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="h-full w-full object-cover"
        style={{ transform: "scaleX(-1)" }} // mirror
      />
      <div className="absolute top-2 right-2 flex gap-2 opacity-0 hover:opacity-100 transition-opacity">
        <Button
          variant="secondary"
          size="icon"
          className="h-8 w-8 rounded-full bg-black/50 text-white hover:bg-black/80 backdrop-blur-sm"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <Minimize2 className="h-4 w-4" />
          ) : (
            <Maximize2 className="h-4 w-4" />
          )}
        </Button>
      </div>
      <div className="absolute bottom-2 left-2 flex items-center gap-1.5 rounded-md bg-black/60 px-2 py-1 backdrop-blur-sm">
        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
        <span className="text-[10px] font-medium text-white tracking-wider uppercase">Live</span>
      </div>
    </div>
  );
}
