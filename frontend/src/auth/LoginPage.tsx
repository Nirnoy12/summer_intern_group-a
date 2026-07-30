import { Card, CardContent } from "@/ui/card";
import { ThemeToggle } from "@/theme/ThemeToggle";
import { AnimatedBackground } from "@/theme/AnimatedBackground";
import { LoginForm } from "./LoginForm";

export default function Login() {
  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <AnimatedBackground />
      <div className="absolute top-4 right-4 z-20">
        <ThemeToggle />
      </div>
      <Card className="w-full max-w-md mx-4 glass-card relative z-10">
        <CardContent className="p-8">
          <h2 className="text-2xl font-semibold text-center text-foreground">Welcome back</h2>
          <p className="text-center text-sm text-muted-foreground mt-2 mb-8">Sign in to continue learning</p>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  );
}