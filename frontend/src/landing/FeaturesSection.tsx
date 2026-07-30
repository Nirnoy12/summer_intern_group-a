import { motion } from "framer-motion";
import { Card, CardHeader, CardTitle, CardDescription } from "@/ui/card";
import { Trophy, Flame, Zap } from "lucide-react";
import { sectionFade } from "./HeroSection";

export function FeaturesSection() {
  return (
    <section id="features" className="relative border-t border-border/10 bg-background/50 py-16 md:py-20 z-10">
      <motion.div {...sectionFade} className="container mx-auto max-w-5xl px-6">
        <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">Features</p>
        <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Everything you need to stay on track.</h2>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Card className="glass-card hover:-translate-y-1">
            <CardHeader>
              <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted"><Trophy className="h-5 w-5 text-foreground" /></div>
              <CardTitle className="text-lg">Earn XP &amp; Level Up</CardTitle>
              <CardDescription>Every video you complete earns Experience Points. Watch your profile level grow as you progress through learning quests.</CardDescription>
            </CardHeader>
          </Card>
          <Card className="glass-card hover:-translate-y-1">
            <CardHeader>
              <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted"><Flame className="h-5 w-5 text-foreground" /></div>
              <CardTitle className="text-lg">Daily Streaks</CardTitle>
              <CardDescription>Consistency is key. Keep your streak alive by learning every day and unlock exclusive badges along the way.</CardDescription>
            </CardHeader>
          </Card>
          <Card className="glass-card hover:-translate-y-1">
            <CardHeader>
              <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted"><Zap className="h-5 w-5 text-foreground" /></div>
              <CardTitle className="text-lg">Instant Import</CardTitle>
              <CardDescription>Paste any YouTube playlist URL and our engine instantly generates a structured, trackable learning quest in seconds.</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </motion.div>
    </section>
  );
}
