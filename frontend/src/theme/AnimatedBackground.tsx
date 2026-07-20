import React, { useEffect, useRef } from 'react';

export const AnimatedBackground: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const particlesContainer = containerRef.current;
    if (!particlesContainer) return;

    const particleCount = 80;
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        createParticle();
    }
    
    function createParticle() {
        if (!particlesContainer) return;
        const particle = document.createElement('div');
        particle.className = 'particle bg-foreground';
        
        // Random size (small)
        const size = Math.random() * 3 + 1;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Initial position
        resetParticle(particle);
        
        particlesContainer.appendChild(particle);
        
        // Animate
        animateParticle(particle);
    }
    
    function resetParticle(particle: HTMLDivElement) {
        // Random position
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        
        particle.style.left = `${posX}%`;
        particle.style.top = `${posY}%`;
        particle.style.opacity = '0';
        
        return {
            x: posX,
            y: posY
        };
    }
    
    function animateParticle(particle: HTMLDivElement) {
        // Initial position
        const pos = resetParticle(particle);
        
        // Random animation properties
        const duration = Math.random() * 10 + 10;
        const delay = Math.random() * 5;
        
        // Animate with GSAP-like timing
        setTimeout(() => {
            if (!particle.isConnected) return; // Cleanup check
            particle.style.transition = `all ${duration}s linear`;
            particle.style.opacity = (Math.random() * 0.3 + 0.1).toString();
            
            // Move in a slight direction
            const moveX = pos.x + (Math.random() * 20 - 10);
            const moveY = pos.y - Math.random() * 30; // Move upwards
            
            particle.style.left = `${moveX}%`;
            particle.style.top = `${moveY}%`;
            
            // Reset after animation completes
            setTimeout(() => {
                if (particle.isConnected) animateParticle(particle);
            }, duration * 1000);
        }, delay * 1000);
    }
    
    // Mouse interaction
    const handleMouseMove = (e: MouseEvent) => {
        if (!particlesContainer) return;
        // Create particles at mouse position
        const mouseX = (e.clientX / window.innerWidth) * 100;
        const mouseY = (e.clientY / window.innerHeight) * 100;
        
        // Create temporary particle
        const particle = document.createElement('div');
        particle.className = 'particle bg-foreground';
        
        // Small size
        const size = Math.random() * 4 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        // Position at mouse
        particle.style.left = `${mouseX}%`;
        particle.style.top = `${mouseY}%`;
        particle.style.opacity = '0.6';
        
        particlesContainer.appendChild(particle);
        
        // Animate outward
        setTimeout(() => {
            particle.style.transition = 'all 2s ease-out';
            particle.style.left = `${mouseX + (Math.random() * 10 - 5)}%`;
            particle.style.top = `${mouseY + (Math.random() * 10 - 5)}%`;
            particle.style.opacity = '0';
            
            // Remove after animation
            setTimeout(() => {
                particle.remove();
            }, 2000);
        }, 10);
        
        // Subtle movement of gradient spheres
        const spheres = document.querySelectorAll<HTMLDivElement>('.gradient-sphere');
        const moveXAmount = (e.clientX / window.innerWidth - 0.5) * 5;
        const moveYAmount = (e.clientY / window.innerHeight - 0.5) * 5;
        
        spheres.forEach(sphere => {
            sphere.style.transform = `translate(${moveXAmount}px, ${moveYAmount}px)`;
        });
    };

    document.addEventListener('mousemove', handleMouseMove);

    return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        if (particlesContainer) particlesContainer.innerHTML = ''; // Cleanup
    };
  }, []);

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
