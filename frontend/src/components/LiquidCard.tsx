import { type ReactNode, useEffect, useRef } from 'react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { VISUAL_CONFIG } from '../config/visual';

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
      <div 
        ref={cardRef}
        className={cn(
          "relative overflow-hidden rounded-3xl",
          "shadow-[0_24px_48px_rgba(0,0,0,0.5),0_0_80px_rgba(0,0,0,0.2)]",
          "before:absolute before:inset-0 before:rounded-3xl before:p-[1px] before:bg-gradient-to-br before:from-white/20 before:via-white/5 before:to-transparent before:[-webkit-mask:linear-gradient(#fff_0_0)_content-box,linear-gradient(#fff_0_0)] before:[-webkit-mask-composite:xor] before:[mask-composite:exclude] before:pointer-events-none",
          "after:absolute after:inset-0 after:rounded-3xl after:shadow-[inset_0_1px_0_rgba(255,255,255,0.18)] after:pointer-events-none",
          className
        )}
        style={{
          ...style,
          backgroundColor: VISUAL_CONFIG.GLASS_TINT,
          backgroundImage: `linear-gradient(145deg, ${VISUAL_CONFIG.GLASS_GRADIENT_START}, ${VISUAL_CONFIG.GLASS_GRADIENT_END})`,
          backdropFilter: `url(#liquid-glass) blur(${VISUAL_CONFIG.GLASS_BLUR_PX}px) saturate(${VISUAL_CONFIG.GLASS_SATURATE}%) brightness(${VISUAL_CONFIG.GLASS_BRIGHTNESS})`,
          WebkitBackdropFilter: `url(#liquid-glass) blur(${VISUAL_CONFIG.GLASS_BLUR_PX}px) saturate(${VISUAL_CONFIG.GLASS_SATURATE}%) brightness(${VISUAL_CONFIG.GLASS_BRIGHTNESS})`,
        }}
      >
        {/* Liquid refraction SVG filter definition (hidden) */}
        <svg className="hidden">
          <defs>
            <filter id="liquid-glass" x="-20%" y="-20%" width="140%" height="140%">
              <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" />
              <feDisplacementMap in="SourceGraphic" in2="noise" scale={VISUAL_CONFIG.GLASS_REFRACTION_SCALE} xChannelSelector="R" yChannelSelector="G" result="displaced" />
              <feBlend in="displaced" in2="SourceGraphic" mode="normal" />
            </filter>
          </defs>
        </svg>

        {/* Dynamic sliding specular highlight (thin edges only) */}
        <div className="absolute inset-0 bg-[linear-gradient(115deg,transparent_45%,rgba(255,255,255,0.06)_50%,transparent_55%)] w-[200%] -translate-x-[50%] animate-[slide-specular_8s_infinite_linear] pointer-events-none mix-blend-overlay" />
        
        {/* Content */}
        <div className="relative z-10 p-8 sm:p-12">
          {children}
        </div>
        
        <style>{`
          @keyframes slide-specular {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(50%); }
          }
        `}</style>
      </div>
    </div>
  );
};

export default LiquidCard;
