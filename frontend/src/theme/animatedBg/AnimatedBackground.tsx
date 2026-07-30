import React, { useRef } from 'react';
import { useParticles } from './useParticles';

export const AnimatedBackground: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  useParticles(containerRef);

  return (
    <div className="fixed top-0 left-0 w-full h-full z-0 overflow-hidden bg-background transition-colors duration-500 pointer-events-none">
      <div className="gradient-background">
        <div className="gradient-sphere sphere-1"></div>
        <div className="gradient-sphere sphere-2"></div>
        <div className="gradient-sphere sphere-3"></div>
      </div>
      <div className="noise-overlay"></div>
      <div className="grid-overlay"></div>
      <div className="glow"></div>
      <div id="particles-container" ref={containerRef} className="particles-container"></div>
    </div>
  );
};
