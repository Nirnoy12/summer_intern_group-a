import { Navbar } from "@/landing/Navbar";
import { Footer } from "@/landing/Footer";
import { AnimatedBackground } from "@/theme/AnimatedBackground";
import { HeroSection } from "./HeroSection";
import { FeaturesSection } from "./FeaturesSection";
import { HowItWorksSection } from "./HowItWorksSection";

export default function Landing() {
  return (
    <div className="min-h-screen text-foreground relative">
      <Navbar />
      <AnimatedBackground />
      <main className="pt-16 relative z-10">
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
      </main>
      <Footer />
    </div>
  );
}
