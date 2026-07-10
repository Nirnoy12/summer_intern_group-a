import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ThemeToggle";

export function Navbar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
      <div className="container mx-auto max-w-6xl px-6 h-16 flex items-center justify-between">
        <Link to="/" className="font-semibold text-lg tracking-tight text-foreground">
          Gamified LMS
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm text-muted-foreground">
          <a href="#features" className="hover:text-foreground transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-foreground transition-colors">How it works</a>
          <a href="#stats" className="hover:text-foreground transition-colors">Stats</a>
        </nav>

        <div className="flex items-center gap-3">
          <ThemeToggle />
          <Link to="/login" className="hidden sm:block">
            <Button variant="ghost" className="text-sm font-medium h-9 px-4">
              Log in
            </Button>
          </Link>
          <Link to="/register">
            <Button className="text-sm font-medium h-9 px-4">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
