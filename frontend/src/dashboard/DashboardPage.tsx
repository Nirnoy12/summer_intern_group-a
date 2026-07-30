import { useState } from "react";
import { Button } from "@/ui/button";
import { Loader2, Plus, LogOut } from "lucide-react";
import { ThemeToggle } from "@/theme/ThemeToggle";
import { AnimatedBackground } from "@/theme/AnimatedBackground";
import { StatsBar } from "./StatsBar";
import { CourseCard } from "./CourseCard";
import { ImportModal } from "./ImportModal";
import { RemoveCourseModal } from "./RemoveCourseModal";
import { useDashboardData } from "./useDashboardData";

export default function Dashboard() {
  const { logout, user, playlists, loading, handleImport, handleRemoveCourse } = useDashboardData();
  const [showModal, setShowModal] = useState(false);
  const [courseToRemove, setCourseToRemove] = useState<string | null>(null);

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-background"><Loader2 className="w-8 h-8 text-primary animate-spin" /></div>;
  if (!user) return <div className="min-h-screen flex flex-col items-center justify-center bg-background space-y-4"><p className="text-xl text-muted-foreground font-semibold">Failed to load user data.</p><Button onClick={logout}>Back to Login</Button></div>;

  return (
    <div className="min-h-screen text-foreground transition-colors duration-300 relative">
      <AnimatedBackground />
      <div className="max-w-5xl mx-auto p-4 sm:p-6 space-y-6 relative z-10">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pt-4">
          <div><h1 className="text-3xl font-semibold tracking-tight text-foreground">Welcome back</h1><p className="text-muted-foreground mt-1">Select a course to continue.</p></div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button onClick={logout} variant="ghost" size="sm" className="flex items-center gap-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10"><LogOut className="h-4 w-4" /><span className="hidden sm:inline">Logout</span></Button>
          </div>
        </header>
        <StatsBar user={user} />
        <div className="pt-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
            <h2 className="text-2xl font-semibold">Your Courses</h2>
            <Button onClick={() => setShowModal(true)}><Plus className="mr-2 h-4 w-4" />Import Playlist</Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {playlists.length === 0 ? (
              <div className="col-span-2 text-center py-16 px-6 rounded-lg border border-dashed border-border"><p className="text-muted-foreground mb-4">No courses yet. Import a playlist to get started.</p><Button onClick={() => setShowModal(true)} variant="outline">Import your first playlist</Button></div>
            ) : (
              playlists.map((playlist) => <CourseCard key={playlist.id} playlist={playlist} onRemove={setCourseToRemove} />)
            )}
          </div>
        </div>
        <ImportModal show={showModal} onClose={() => setShowModal(false)} onImport={async (url) => { await handleImport(url); setShowModal(false); }} />
        <RemoveCourseModal courseId={courseToRemove} onClose={() => setCourseToRemove(null)} onConfirm={async (id) => { await handleRemoveCourse(id); setCourseToRemove(null); }} />
      </div>
    </div>
  );
}