import { Link } from "react-router-dom";

export function Footer() {
  return (
    <footer className="relative z-10 border-t border-border/20 bg-background/80 backdrop-blur-xl py-12 mt-auto">
      <div className="container mx-auto max-w-6xl px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="col-span-2 md:col-span-1">
            <Link to="/" className="font-semibold text-foreground">
              Gamified LMS
            </Link>
            <p className="text-sm text-muted-foreground mt-3 max-w-xs leading-relaxed">
              Turn YouTube playlists into structured learning paths.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-foreground mb-4">Platform</h4>
            <ul className="space-y-2.5">
              <li><a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a></li>
              <li><a href="#how-it-works" className="text-sm text-muted-foreground hover:text-foreground transition-colors">How it Works</a></li>
              <li><a href="#stats" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Stats</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-medium text-foreground mb-4">Company</h4>
            <ul className="space-y-2.5">
              <li><a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">About</a></li>
              <li><a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Privacy</a></li>
              <li><a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Terms</a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-medium text-foreground mb-4">Connect</h4>
            <ul className="space-y-2.5">
              <li><a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Twitter / X</a></li>
              <li><a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">GitHub</a></li>
              <li><a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Discord</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-border flex flex-col sm:flex-row justify-between items-center gap-3">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Gamified LMS. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
