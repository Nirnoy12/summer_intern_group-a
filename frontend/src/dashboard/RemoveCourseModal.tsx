import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/ui/card";
import { Button } from "@/ui/button";
import { Loader2, X, Trash } from "lucide-react";

export function RemoveCourseModal({ courseId, onClose, onConfirm }: { courseId: string | null; onClose: () => void; onConfirm: (id: string) => Promise<void> }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!courseId) return null;

  const handleConfirm = async () => {
    setLoading(true);
    setError("");
    try {
      await onConfirm(courseId);
    } catch (err: any) {
      setError(err.message || "Failed to remove");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <Card className="w-full max-w-md relative glass-card border-destructive/50">
        <button onClick={onClose} className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors" disabled={loading}>
          <X className="h-5 w-5" />
        </button>
        <CardHeader>
          <CardTitle className="text-xl text-destructive flex items-center gap-2">
            <Trash className="h-5 w-5" /> Remove Course
          </CardTitle>
          <CardDescription>Are you sure you want to remove this course? This action cannot be undone and will delete all your progress.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && <div className="text-sm text-destructive bg-destructive/10 border border-destructive/20 p-3 rounded-md">{error}</div>}
          <div className="flex gap-3 mt-4">
            <Button onClick={onClose} variant="outline" className="flex-1" disabled={loading}>Cancel</Button>
            <Button onClick={handleConfirm} variant="destructive" className="flex-1" disabled={loading}>
              {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Yes, Remove"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
