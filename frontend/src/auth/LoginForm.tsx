import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "@/auth/auth";
import { useAuth } from "@/auth/AuthContext";
import { Button } from "@/ui/button";
import { Input } from "@/ui/input";
import { Eye, EyeOff, Loader2, Mail, Lock, CheckCircle, AlertCircle } from "lucide-react";

export function LoginForm() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true); setSuccess(""); setError("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);
      const response = await API.post("/api/auth/login", formData, { headers: { "Content-Type": "application/x-www-form-urlencoded" } });
      login(response.data.access_token);
      setSuccess("Login successful! Redirecting to dashboard...");
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleLogin} className="space-y-5">
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input type="email" placeholder="you@example.com" value={email} onChange={(e) => setEmail(e.target.value)} className="pl-10 h-10" required />
          </div>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-foreground">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input type={showPassword ? "text" : "password"} placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} className="pl-10 pr-10 h-10" required />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3 text-muted-foreground hover:text-foreground transition-colors">
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
        {success && <div className="flex items-center gap-2 rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700 dark:border-green-800 dark:bg-green-950 dark:text-green-400"><CheckCircle size={16} className="shrink-0" /><span>{success}</span></div>}
        {error && <div className="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive"><AlertCircle size={16} className="shrink-0" /><span>{error}</span></div>}
        <Button type="submit" disabled={loading} className="w-full h-10">
          {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Signing in…</> : "Sign in"}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted-foreground">Don't have an account? <Link to="/register" className="font-medium text-primary hover:text-primary/80 transition-colors">Create one</Link></p>
    </>
  );
}
