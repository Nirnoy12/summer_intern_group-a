import { useEffect, useState } from "react";
import API from "@/auth/auth";
import { useAuth } from "@/auth/AuthContext";

export function useDashboardData() {
  const { token, logout } = useAuth();
  const [user, setUser] = useState<any>(null);
  const [playlists, setPlaylists] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [userRes, playlistsRes] = await Promise.all([
        API.get("/api/users/me", { headers: { Authorization: `Bearer ${token}` } }),
        API.get("/api/playlists", { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      setUser(userRes.data);
      setPlaylists(playlistsRes.data);
    } catch (err: any) {
      if (err.response?.status === 401) logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  const handleImport = async (importUrl: string) => {
    let playlistId = "";
    try {
      const urlObj = new URL(importUrl);
      playlistId = urlObj.searchParams.get("list") || "";
    } catch {
      throw new Error("Invalid URL format. Please paste a valid YouTube link.");
    }
    if (!playlistId) throw new Error("Could not find a 'list' parameter in the URL.");

    try {
      await API.post("/api/ingest/playlist", { playlist_id: playlistId }, { headers: { Authorization: `Bearer ${token}` } });
      await fetchData();
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || "Failed to import playlist.");
    }
  };

  const handleRemoveCourse = async (playlistId: string) => {
    try {
      await API.delete(`/api/playlists/${playlistId}`, { headers: { Authorization: `Bearer ${token}` } });
      setPlaylists((prev) => prev.filter((p) => p.id !== playlistId));
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || "Failed to remove course.");
    }
  };

  return { token, logout, user, playlists, loading, handleImport, handleRemoveCourse };
}
