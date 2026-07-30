import { Link } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/ui/card";
import { Badge } from "@/ui/badge";
import { Button } from "@/ui/button";
import { Progress } from "@/ui/progress";
import { PlayCircle, Trash } from "lucide-react";

export function CourseCard({ playlist, onRemove }: { playlist: any; onRemove: (id: string) => void }) {
  const progress = playlist.course_progress_percentage || 0;
  const status = playlist.status || "Not Started";

  return (
    <Card className="glass-card flex flex-col hover:-translate-y-1 hover:border-primary/30 overflow-hidden">
      <div className="h-40 w-full overflow-hidden bg-muted">
        <img
          src={playlist.thumbnail_url || "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80"}
          alt="Course Thumbnail"
          className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
        />
      </div>
      <CardHeader className="pt-5">
        <div className="flex justify-between items-start mb-2">
          <div className="flex gap-2">
            <Badge variant="secondary">{playlist.video_count} Videos</Badge>
            {status === "Completed" && <Badge className="bg-green-600 hover:bg-green-700 text-white">Completed</Badge>}
            {status === "In Progress" && <Badge variant="outline" className="text-blue-500 border-blue-500">In Progress</Badge>}
            {status === "Not Started" && <Badge variant="outline" className="text-muted-foreground border-border">Not Started</Badge>}
          </div>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-destructive hover:bg-destructive/10" onClick={(e) => { e.preventDefault(); onRemove(playlist.id); }}>
            <Trash className="h-4 w-4" />
          </Button>
        </div>
        <CardTitle className="text-lg line-clamp-1">{playlist.title}</CardTitle>
        <CardDescription className="mt-1 line-clamp-2">{playlist.description}</CardDescription>
      </CardHeader>
      <CardContent className="mt-auto pt-2 pb-6">
        <div className="flex justify-between items-center text-sm mb-2">
          <span className="text-muted-foreground">{playlist.completed_videos} / {playlist.video_count} completed</span>
          <span className="font-semibold">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-2 mb-2" />
        {playlist.last_accessed_date && (
          <div className="text-[10px] text-muted-foreground text-right mb-4">
            Last accessed: {new Date(playlist.last_accessed_date).toLocaleDateString()}
          </div>
        )}
        {!playlist.last_accessed_date && <div className="h-4 mb-4" />}
        <Link to={`/playlist/${playlist.id}`} className="block w-full">
          <Button className="w-full active:scale-95 transition-transform" variant="default">
            <PlayCircle className="mr-2 h-4 w-4" /> Continue
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
