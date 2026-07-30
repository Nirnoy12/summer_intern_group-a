import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Button } from "@/ui/button";
import { Separator } from "@/ui/separator";
import { Search, Zap, Rocket, ArrowRight } from "lucide-react";
import { sectionFade } from "./HeroSection";

export function HowItWorksSection() {
  return (
    <>
      <section id="how-it-works" className="relative border-t border-border/10 bg-background/50 py-16 md:py-20 z-10">
        <motion.div {...sectionFade} className="container mx-auto max-w-3xl px-6">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">How it works</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">Three steps to mastery.</h2>
          <div className="mt-8 space-y-0">
            {[
              { num: "01", icon: Search, title: "Find a playlist", desc: "Browse YouTube for any educational playlist. Machine learning, guitar lessons, cooking — anything goes." },
              { num: "02", icon: Zap, title: "Import & generate", desc: "Paste the playlist URL into your dashboard. We break it down into trackable lessons with XP rewards in seconds." },
              { num: "03", icon: Rocket, title: "Learn, earn, repeat", desc: "Watch videos on our platform, mark them complete, earn XP, maintain your streak, and watch your level soar." },
            ].map((step, i, arr) => (
              <div key={step.num}>
                <div className="flex gap-4 py-6">
                  <div className="flex flex-col items-center pt-1"><div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-border bg-muted"><step.icon className="h-5 w-5 text-foreground" /></div></div>
                  <div><p className="text-xs font-medium text-muted-foreground">{step.num}</p><h3 className="mt-1 text-xl font-semibold tracking-tight">{step.title}</h3><p className="mt-2 text-muted-foreground leading-relaxed">{step.desc}</p></div>
                </div>
                {i < arr.length - 1 && <Separator />}
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      <section id="stats" className="relative border-t border-border/10 bg-background/50 py-12 md:py-16 z-10">
        <motion.div {...sectionFade} className="container mx-auto max-w-5xl px-6">
          <div className="grid grid-cols-2 gap-8 md:grid-cols-4 md:gap-12">
            {[
              { value: "10K+", label: "Active learners" },
              { value: "50K+", label: "Courses completed" },
              { value: "1.2M", label: "XP earned" },
              { value: "98%", label: "Satisfaction rate" },
            ].map((stat) => (
              <div key={stat.label} className="text-center"><p className="text-3xl font-bold tracking-tight sm:text-4xl">{stat.value}</p><p className="mt-1 text-sm text-muted-foreground">{stat.label}</p></div>
            ))}
          </div>
        </motion.div>
      </section>

      <section className="relative border-t border-border/10 bg-background/50 py-16 md:py-20 z-10">
        <motion.div {...sectionFade} className="container mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Ready to start learning?</h2>
          <p className="mx-auto mt-4 max-w-md text-muted-foreground leading-relaxed">Join thousands of learners who transformed their YouTube binge sessions into structured skill-building journeys.</p>
          <div className="mt-10"><Link to="/dashboard"><Button size="lg" className="h-12 px-6 text-base font-medium active:scale-95 transition-transform">Start Learning <ArrowRight className="ml-2 h-4 w-4" /></Button></Link></div>
        </motion.div>
      </section>
    </>
  );
}
