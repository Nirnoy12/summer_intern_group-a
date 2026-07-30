import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "@/auth/auth";
import { Button } from "@/ui/button";
import { Input } from "@/ui/input";
import { Eye, EyeOff, Loader2, Mail, Lock, CheckCircle, AlertCircle } from "lucide-react";

export function RegisterForm() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true); setSuccess(""); setError("");
    try {
      await API.post("/api/auth/register", { email, password });
      setSuccess("Registration successful! Redirecting to Login...");
      setTimeout(() => navigate("/login"), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to connect to server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={handleRegister} className="space-y-5">
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
            <Input type={showPassword ? "text" : "password"} placeholder="Create a password" value={password} onChange={(e) => setPassword(e.target.value)} className="pl-10 pr-10 h-10" required />
            <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-3 text-muted-foreground hover:text-foreground transition-colors">
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
        {success && <div className="flex items-center gap-2 rounded-md border border-green-500/30 bg-green-500/10 p-3 text-sm text-green-600 dark:text-green-400"><CheckCircle size={16} /><span>{success}</span></div>}
        {error && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive"><AlertCircle size={16} /><span>{error}</span></div>}
        <Button type="submit" disabled={loading} className="w-full h-10">
          {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Creating account…</> : "Create account"}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted-foreground">Already have an account? <Link to="/login" className="font-medium text-primary hover:text-primary/80 transition-colors">Log in</Link></p>
    </>
  );
}
