import { ReactNode } from 'react';
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
  return (
    <div 
      className={cn(
        "relative overflow-hidden rounded-3xl border border-white/10 bg-black/40 backdrop-blur-xl",
        "shadow-[0_8px_32px_0_rgba(230,74,25,0.1)]", // subtle ember shadow
        className
      )}
      style={style}
    >
      {/* Liquid refraction SVG filter definition (hidden) */}
      <svg className="hidden">
        <defs>
          <filter id="liquid">
            <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="3" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="5" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>
      
      {/* Dynamic reflex highlight */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-transparent opacity-50 mix-blend-overlay pointer-events-none" />
      <div className="absolute -inset-[100%] bg-gradient-to-r from-transparent via-white/5 to-transparent rotate-45 translate-x-[-100%] animate-[shimmer_3s_infinite] pointer-events-none" />

      {/* Content */}
      <div className="relative z-10 p-8 sm:p-12">
        {children}
      </div>
      
      {/* Global shimmer keyframes added in tailwind config or arbitrary style */}
      <style>{`
        @keyframes shimmer {
          100% { transform: translateX(100%) rotate(45deg); }
        }
      `}</style>
    </div>
  );
};

export default LiquidCard;
