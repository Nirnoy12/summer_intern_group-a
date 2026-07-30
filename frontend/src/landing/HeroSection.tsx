import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Button } from "@/ui/button";
import { ArrowRight } from "lucide-react";

export const sectionFade = {
  initial: { opacity: 0 },
  whileInView: { opacity: 1 },
  viewport: { once: true, margin: "-60px" } as const,
  transition: { duration: 0.6 },
};

export function HeroSection() {
  return (
    <section className="relative flex min-h-[calc(100svh-4rem)] items-center justify-center overflow-hidden">
      <div className="hero-wave-wrapper">
        <div className="hero-wave"><span></span><span></span><span></span></div>
      </div>
      <motion.div {...sectionFade} className="container mx-auto max-w-4xl px-6 py-12 text-center relative z-10">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          Learn anything. Level up everything.
        </h1>
        <p className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground leading-relaxed">
          Transform any YouTube playlist into a structured learning quest. Earn XP, maintain streaks, and watch your skills compound over time.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link to="/dashboard">
            <Button size="lg" className="h-12 px-6 text-base font-medium active:scale-95 transition-transform">
              Start Learning <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <a href="#how-it-works">
            <Button variant="ghost" size="lg" className="h-12 px-6 text-base font-medium active:scale-95 transition-transform">
              See how it works
            </Button>
          </a>
        </div>
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4 opacity-90">
          {[
            { title: "Advanced Web Development", xp: "+500 XP", img: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&q=80" },
            { title: "Machine Learning Basics", xp: "+850 XP", img: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80" },
            { title: "Productivity Masterclass", xp: "+300 XP", img: "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=800&q=80" }
          ].map((course, idx) => (
            <div key={idx} className={`glass-card rounded-xl overflow-hidden ${idx === 1 ? 'md:-translate-y-4' : ''}`}>
              <div className="h-32 w-full bg-muted"><img src={course.img} alt={course.title} className="w-full h-full object-cover" /></div>
              <div className="p-4 text-left">
                <h3 className="font-semibold text-sm line-clamp-1">{course.title}</h3>
                <p className="text-xs text-primary mt-1 font-medium">{course.xp}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  );
}
