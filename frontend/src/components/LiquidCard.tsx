import { type ReactNode, useEffect, useRef } from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface LiquidCardProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

const LiquidCard = ({ children, className, style }: LiquidCardProps) => {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!cardRef.current) return;
      const rect = cardRef.current.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      cardRef.current.style.setProperty('--mx', `${x}px`);
      cardRef.current.style.setProperty('--my', `${y}px`);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div className="relative group/card w-full">
      {/* Backlight orbs */}
      <div className="absolute inset-[-50px] -z-10 overflow-hidden rounded-full opacity-30 blur-3xl pointer-events-none mix-blend-screen">
        <div className="absolute top-[10%] left-[20%] w-[120px] h-[120px] bg-ember-500 rounded-full animate-[drift_8s_ease-in-out_infinite_alternate]" />
        <div className="absolute top-[60%] right-[10%] w-[150px] h-[150px] bg-ember-600 rounded-full animate-[drift_12s_ease-in-out_infinite_alternate-reverse]" />
        <div className="absolute bottom-[20%] left-[40%] w-[200px] h-[200px] bg-[#ff8a1f] rounded-full animate-[drift_10s_ease-in-out_infinite_alternate]" />
        <div className="absolute top-[40%] left-[60%] w-[100px] h-[100px] bg-red-600 rounded-full animate-[drift_14s_ease-in-out_infinite_alternate-reverse]" />
      </div>

      <div 
        ref={cardRef}
        className={cn(
          "relative overflow-hidden rounded-3xl",
          "shadow-[0_24px_48px_rgba(0,0,0,0.5),0_0_80px_rgba(230,74,25,0.05)]",
          "bg-[linear-gradient(145deg,rgba(255,255,255,0.14),rgba(255,255,255,0.04))]",
          "[backdrop-filter:blur(32px)_saturate(200%)_brightness(1.15)] [-webkit-backdrop-filter:blur(32px)_saturate(200%)_brightness(1.15)]",
          "before:absolute before:inset-0 before:rounded-3xl before:p-[1px] before:bg-gradient-to-br before:from-white/40 before:via-white/5 before:to-white/20 before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:pointer-events-none",
          "after:absolute after:inset-0 after:rounded-3xl after:shadow-[inset_0_1px_0_rgba(255,255,255,0.45),inset_0_0_0_1px_rgba(255,255,255,0.05),inset_0_-24px_48px_rgba(255,120,60,0.07)] after:pointer-events-none",
          className
        )}
        style={{
          ...style,
          // CSS fallback for browsers that don't support the SVG filter well
          backdropFilter: "url(#liquid-glass) blur(32px) saturate(200%) brightness(1.15)",
          WebkitBackdropFilter: "url(#liquid-glass) blur(32px) saturate(200%) brightness(1.15)",
        }}
      >
        {/* Liquid refraction SVG filter definition (hidden) */}
        <svg className="hidden">
          <defs>
            <filter id="liquid-glass" x="-20%" y="-20%" width="140%" height="140%">
              <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" />
              <feDisplacementMap in="SourceGraphic" in2="noise" scale="35" xChannelSelector="R" yChannelSelector="G" result="displaced" />
              <feComponentTransfer in="displaced" result="chromatic">
                 <feFuncR type="linear" slope="1.05"/>
                 <feFuncG type="linear" slope="1.0"/>
                 <feFuncB type="linear" slope="0.95"/>
              </feComponentTransfer>
              <feBlend in="chromatic" in2="SourceGraphic" mode="normal" />
            </filter>
          </defs>
        </svg>

        {/* Dynamic sliding specular highlight */}
        <div className="absolute inset-0 bg-[linear-gradient(115deg,transparent_20%,rgba(255,255,255,0.14)_50%,transparent_80%)] w-[200%] -translate-x-[50%] animate-[slide-specular_6s_infinite_linear] pointer-events-none mix-blend-overlay opacity-70" />
        
        {/* Radial highlight following cursor */}
        <div 
          className="absolute inset-0 pointer-events-none opacity-0 group-hover/card:opacity-100 transition-opacity duration-500"
          style={{
            background: 'radial-gradient(circle 250px at var(--mx, 50%) var(--my, 50%), rgba(255,255,255,0.15), transparent 80%)'
          }}
        />

        {/* Content */}
        <div className="relative z-10 p-8 sm:p-12">
          {children}
        </div>
        
        <style>{`
          @keyframes slide-specular {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(50%); }
          }
          @keyframes drift {
            0% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -50px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.9); }
            100% { transform: translate(0, 0) scale(1); }
          }
        `}</style>
      </div>
    </div>
  );
};

export default LiquidCard;
