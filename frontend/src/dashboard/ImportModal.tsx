import { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/ui/card";
import { Button } from "@/ui/button";
import { Loader2, X } from "lucide-react";

export function ImportModal({ show, onClose, onImport }: { show: boolean; onClose: () => void; onImport: (url: string) => Promise<void> }) {
  const [importUrl, setImportUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!show) return null;

  const handleImport = async () => {
    setError("");
    if (!importUrl) { setError("Please enter a URL"); return; }
    setLoading(true);
    try {
      await onImport(importUrl);
      setImportUrl("");
    } catch (err: any) {
      setError(err.message || "Failed to import");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm p-4">
      <Card className="w-full max-w-md relative glass-card">
        <button onClick={onClose} className="absolute top-4 right-4 text-muted-foreground hover:text-foreground transition-colors">
          <X className="h-5 w-5" />
        </button>
        <CardHeader>
          <CardTitle className="text-xl">Import Playlist</CardTitle>
          <CardDescription>Paste a YouTube playlist link to import a new course.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium text-muted-foreground mb-2 block">YouTube Link</label>
            <input type="text" placeholder="https://youtube.com/playlist?list=..." value={importUrl} onChange={(e) => setImportUrl(e.target.value)} className="w-full bg-background border border-input rounded-md px-3 py-2 text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors" />
          </div>
          {error && <div className="text-sm text-destructive bg-destructive/10 border border-destructive/20 p-3 rounded-md">{error}</div>}
          <Button onClick={handleImport} disabled={loading} className="w-full" variant="default">
            {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Importing...</> : "Import Course"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
