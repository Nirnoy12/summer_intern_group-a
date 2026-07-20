import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Button } from "@/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/ui/card";
import { Separator } from "@/ui/separator";
import { Navbar } from "@/landing/Navbar";
import { Footer } from "@/landing/Footer";
import { AnimatedBackground } from "@/theme/AnimatedBackground";
import { ArrowRight, Trophy, Flame, Zap, Search, Rocket } from "lucide-react";

const sectionFade = {
  initial: { opacity: 0 },
  whileInView: { opacity: 1 },
  viewport: { once: true, margin: "-60px" } as const,
  transition: { duration: 0.6 },
};

export default function Landing() {
  return (
    <div className="min-h-screen text-foreground relative">
      <Navbar />

      {/* Animated Space Background */}
      <AnimatedBackground />

      <main className="pt-16 relative z-10">
        {/* ──── Hero ──── */}
        <section className="relative flex min-h-[calc(100svh-4rem)] items-center justify-center overflow-hidden">
          {/* Wavy Animation Transition at Bottom */}
          <div className="hero-wave-wrapper">
            <div className="hero-wave">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>

          <motion.div {...sectionFade} className="container mx-auto max-w-4xl px-6 py-12 text-center relative z-10">
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              Learn anything. Level up everything.
            </h1>

            <p className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground leading-relaxed">
              Transform any YouTube playlist into a structured learning quest.
              Earn XP, maintain streaks, and watch your skills compound over time.
            </p>

            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link to="/dashboard">
                <Button size="lg" className="h-12 px-6 text-base font-medium active:scale-95 transition-transform">
                  Start Learning
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <a href="#how-it-works">
                <Button variant="ghost" size="lg" className="h-12 px-6 text-base font-medium active:scale-95 transition-transform">
                  See how it works
                </Button>
              </a>
            </div>

            {/* LMS Course Thumbnails Visual */}
            <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 opacity-90">
              {[
                { title: "Advanced Web Development", xp: "+500 XP", img: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80" },
                { title: "Machine Learning Basics", xp: "+850 XP", img: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80" },
                { title: "Productivity Masterclass", xp: "+300 XP", img: "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=800&q=80" }
              ].map((course, idx) => (
                <div key={idx} className={`glass-card rounded-xl overflow-hidden ${idx === 1 ? 'md:-translate-y-4' : ''}`}>
                  <div className="h-32 w-full bg-muted">
                    <img src={course.img} alt={course.title} className="w-full h-full object-cover" />
                  </div>
                  <div className="p-4 text-left">
                    <h3 className="font-semibold text-sm line-clamp-1">{course.title}</h3>
                    <p className="text-xs text-primary mt-1 font-medium">{course.xp}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </section>

        {/* ──── Features ──── */}
        <section id="features" className="relative border-t border-border/10 bg-background/50 py-16 md:py-20 z-10">
          <motion.div {...sectionFade} className="container mx-auto max-w-5xl px-6">
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">
              Features
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Everything you need to stay on track.
            </h2>

            <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {/* Card 1 */}
              <Card className="glass-card hover:-translate-y-1">
                <CardHeader>
                  <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted">
                    <Trophy className="h-5 w-5 text-foreground" />
                  </div>
                  <CardTitle className="text-lg">Earn XP &amp; Level Up</CardTitle>
                  <CardDescription>
                    Every video you complete earns Experience Points. Watch your profile level grow as you progress through learning quests.
                  </CardDescription>
                </CardHeader>
              </Card>

              {/* Card 2 */}
              <Card className="glass-card hover:-translate-y-1">
                <CardHeader>
                  <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted">
                    <Flame className="h-5 w-5 text-foreground" />
                  </div>
                  <CardTitle className="text-lg">Daily Streaks</CardTitle>
                  <CardDescription>
                    Consistency is key. Keep your streak alive by learning every day and unlock exclusive badges along the way.
                  </CardDescription>
                </CardHeader>
              </Card>

              {/* Card 3 */}
              <Card className="glass-card hover:-translate-y-1">
                <CardHeader>
                  <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-muted">
                    <Zap className="h-5 w-5 text-foreground" />
                  </div>
                  <CardTitle className="text-lg">Instant Import</CardTitle>
                  <CardDescription>
                    Paste any YouTube playlist URL and our engine instantly generates a structured, trackable learning quest in seconds.
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </motion.div>
        </section>

        {/* ──── How It Works ──── */}
        <section id="how-it-works" className="relative border-t border-border/10 bg-background/50 py-16 md:py-20 z-10">
          <motion.div {...sectionFade} className="container mx-auto max-w-3xl px-6">
            <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">
              How it works
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Three steps to mastery.
            </h2>

            <div className="mt-8 space-y-0">
              {[
                {
                  num: "01",
                  icon: Search,
                  title: "Find a playlist",
                  desc: "Browse YouTube for any educational playlist. Machine learning, guitar lessons, cooking — anything goes.",
                },
                {
                  num: "02",
                  icon: Zap,
                  title: "Import & generate",
                  desc: "Paste the playlist URL into your dashboard. We break it down into trackable lessons with XP rewards in seconds.",
                },
                {
                  num: "03",
                  icon: Rocket,
                  title: "Learn, earn, repeat",
                  desc: "Watch videos on our platform, mark them complete, earn XP, maintain your streak, and watch your level soar.",
                },
              ].map((step, i, arr) => (
                <div key={step.num}>
                  <div className="flex gap-4 py-6">
                    <div className="flex flex-col items-center pt-1">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border bg-muted">
                        <step.icon className="h-5 w-5 text-foreground" />
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">{step.num}</p>
                      <h3 className="mt-1 text-xl font-semibold tracking-tight">{step.title}</h3>
                      <p className="mt-2 text-muted-foreground leading-relaxed">{step.desc}</p>
                    </div>
                  </div>
                  {i < arr.length - 1 && <Separator />}
                </div>
              ))}
            </div>
          </motion.div>
        </section>

        {/* ──── Stats ──── */}
        <section id="stats" className="relative border-t border-border/10 bg-background/50 py-12 md:py-16 z-10">
          <motion.div {...sectionFade} className="container mx-auto max-w-5xl px-6">
            <div className="grid grid-cols-2 gap-8 md:grid-cols-4 md:gap-12">
              {[
                { value: "10K+", label: "Active learners" },
                { value: "50K+", label: "Courses completed" },
                { value: "1.2M", label: "XP earned" },
                { value: "98%", label: "Satisfaction rate" },
              ].map((stat) => (
                <div key={stat.label} className="text-center">
                  <p className="text-3xl font-bold tracking-tight sm:text-4xl">{stat.value}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </section>

        {/* ──── Final CTA ──── */}
        <section className="relative border-t border-border/10 bg-background/50 py-16 md:py-20 z-10">
          <motion.div {...sectionFade} className="container mx-auto max-w-2xl px-6 text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Ready to start learning?
            </h2>
            <p className="mx-auto mt-4 max-w-md text-muted-foreground leading-relaxed">
              Join thousands of learners who transformed their YouTube binge sessions into structured skill-building journeys.
            </p>
            <div className="mt-10">
              <Link to="/dashboard">
                <Button size="lg" className="h-12 px-6 text-base font-medium active:scale-95 transition-transform">
                  Start Learning
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
