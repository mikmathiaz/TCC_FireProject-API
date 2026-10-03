import React, { useEffect, useRef } from 'react';
import {
  HEAT_GRID_W,
  HEAT_GRID_H,
  HEAT_RADIUS_PX,
  HEAT_COOL_SECONDS,
  HEAT_DIFFUSION,
  HEAT_CLICK_MULT,
  HEAT_MIN_INTENSITY,
} from '../config/visual';

// Precomputed 256-step Thermal Rainbow LUT (#050a2e -> #0a1a8c -> #1e6bff -> #12d4e8 -> #2ee65a -> #f5ee28 -> #ff9a1a -> #ff2a1a -> #ff8fa8 -> #ffffff)
const THERMAL_STOPS = [
  { t: 0.00, r: 5,   g: 10,  b: 46 },  // #050a2e (deep navy)
  { t: 0.08, r: 10,  g: 26,  b: 140 }, // #0a1a8c (dark blue)
  { t: 0.20, r: 30,  g: 107, b: 255 }, // #1e6bff (cobalt blue)
  { t: 0.35, r: 18,  g: 212, b: 232 }, // #12d4e8 (cyan)
  { t: 0.49, r: 46,  g: 230, b: 90 },  // #2ee65a (green)
  { t: 0.63, r: 245, g: 238, b: 40 },  // #f5ee28 (yellow)
  { t: 0.76, r: 255, g: 154, b: 26 },  // #ff9a1a (orange)
  { t: 0.88, r: 255, g: 42,  b: 26 },  // #ff2a1a (red)
  { t: 0.95, r: 255, g: 143, b: 168 }, // #ff8fa8 (light pink)
  { t: 1.00, r: 255, g: 255, b: 255 }, // #ffffff (white hot)
];

function smoothstep(min: number, max: number, value: number): number {
  const x = Math.max(0, Math.min(1, (value - min) / (max - min)));
  return x * x * (3 - 2 * x);
}

// Endianness check for Uint32 packed colors
const isLittleEndian = (() => {
  const buf = new ArrayBuffer(4);
  const u32 = new Uint32Array(buf);
  const u8 = new Uint8Array(buf);
  u32[0] = 0x12345678;
  return u8[0] === 0x78;
})();

const LUT_32 = new Uint32Array(256);

// Build LUT once
for (let i = 0; i < 256; i++) {
  const t = i / 255;
  let idx = 0;
  while (idx < THERMAL_STOPS.length - 1 && THERMAL_STOPS[idx + 1].t < t) {
    idx++;
  }
  const s0 = THERMAL_STOPS[idx];
  const s1 = THERMAL_STOPS[Math.min(idx + 1, THERMAL_STOPS.length - 1)];
  const range = s1.t - s0.t || 1;
  const f = Math.max(0, Math.min(1, (t - s0.t) / range));

  const r = Math.round(s0.r + (s1.r - s0.r) * f);
  const g = Math.round(s0.g + (s1.g - s0.g) * f);
  const b = Math.round(s0.b + (s1.b - s0.b) * f);
  const a = Math.round(smoothstep(0.03, 0.22, t) * 255);

  if (isLittleEndian) {
    LUT_32[i] = (a << 24) | (b << 16) | (g << 8) | r;
  } else {
    LUT_32[i] = (r << 24) | (g << 16) | (b << 8) | a;
  }
}

export const ThermalMouseCanvas: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { willReadFrequently: false });
    if (!ctx) return;

    const W = HEAT_GRID_W;
    const H = HEAT_GRID_H;
    const totalCells = W * H;

    // Fixed low-resolution internal grid for soft, blurred thermal camera look
    canvas.width = W;
    canvas.height = H;

    let heatGrid = new Float32Array(totalCells);
    let nextGrid = new Float32Array(totalCells);
    const imgData = ctx.createImageData(W, H);
    const data32 = new Uint32Array(imgData.data.buffer);

    let lastPointerX: number | null = null;
    let lastPointerY: number | null = null;
    let lastTime = performance.now();
    let hasHeat = false;
    let isRunning = false;
    let animFrameId = 0;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const coolSeconds = reducedMotion ? 1.2 : HEAT_COOL_SECONDS;
    const baseIntensity = reducedMotion ? HEAT_MIN_INTENSITY * 0.5 : HEAT_MIN_INTENSITY;

    // Stamp heat with gaussian falloff in screen pixel radius
    const stampHeat = (screenX: number, screenY: number, radiusPx: number, intensity: number) => {
      const winW = window.innerWidth || 1;
      const winH = window.innerHeight || 1;

      const minX = Math.max(0, Math.floor(((screenX - radiusPx) / winW) * W));
      const maxX = Math.min(W - 1, Math.ceil(((screenX + radiusPx) / winW) * W));
      const minY = Math.max(0, Math.floor(((screenY - radiusPx) / winH) * H));
      const maxY = Math.min(H - 1, Math.ceil(((screenY + radiusPx) / winH) * H));

      const cellW = winW / W;
      const cellH = winH / H;
      const sigma = radiusPx * 0.42;
      const twoSigmaSq = 2 * sigma * sigma;

      for (let y = minY; y <= maxY; y++) {
        const cellY = (y + 0.5) * cellH;
        const dy = cellY - screenY;
        const dySq = dy * dy;
        const rowOffset = y * W;

        for (let x = minX; x <= maxX; x++) {
          const cellX = (x + 0.5) * cellW;
          const dx = cellX - screenX;
          const dSq = dx * dx + dySq;

          if (dSq <= radiusPx * radiusPx) {
            const falloff = Math.exp(-dSq / twoSigmaSq);
            const idx = rowOffset + x;
            heatGrid[idx] = Math.min(1.0, heatGrid[idx] + falloff * intensity);
          }
        }
      }

      hasHeat = true;
      if (!isRunning) {
        startLoop();
      }
    };

    // Pointer move listener with continuous interpolation
    const handlePointerMove = (e: PointerEvent) => {
      const curX = e.clientX;
      const curY = e.clientY;
      const now = performance.now();
      const dt = Math.max(1, now - lastTime);

      if (lastPointerX === null || lastPointerY === null) {
        lastPointerX = curX;
        lastPointerY = curY;
        lastTime = now;
        stampHeat(curX, curY, HEAT_RADIUS_PX, baseIntensity);
        return;
      }

      const dx = curX - lastPointerX;
      const dy = curY - lastPointerY;
      const dist = Math.hypot(dx, dy);
      const speed = dist / dt; // pixels per ms

      // Intensity grows with speed (min 0.35, max 1.0)
      const intensity = Math.min(1.0, Math.max(baseIntensity, speed * 0.45));

      // Interpolate steps to guarantee a seamless, non-dotted heat trail
      const stepSize = Math.max(10, HEAT_RADIUS_PX * 0.25);
      const steps = Math.max(1, Math.ceil(dist / stepSize));

      for (let s = 1; s <= steps; s++) {
        const interpX = lastPointerX + (dx * s) / steps;
        const interpY = lastPointerY + (dy * s) / steps;
        stampHeat(interpX, interpY, HEAT_RADIUS_PX, intensity);
      }

      lastPointerX = curX;
      lastPointerY = curY;
      lastTime = now;
    };

    // Click / touch: strong pulse (value 1.0, larger radius ~1.6x)
    const handlePointerDown = (e: PointerEvent) => {
      stampHeat(e.clientX, e.clientY, HEAT_RADIUS_PX * HEAT_CLICK_MULT, 1.0);
    };

    const handlePointerLeave = () => {
      lastPointerX = null;
      lastPointerY = null;
    };

    // Simulation & render loop (cooling + 3x3 diffusion)
    let prevFrameTime = performance.now();

    const loop = (currentTime: number) => {
      if (document.visibilityState === 'hidden') {
        isRunning = false;
        return;
      }

      const dt = Math.min(0.08, (currentTime - prevFrameTime) / 1000);
      prevFrameTime = currentTime;

      const decay = dt / coolSeconds;
      const diff = HEAT_DIFFUSION;
      let maxHeat = 0;

      // 3x3 subtle diffusion and clean linear cooling decay
      for (let y = 0; y < H; y++) {
        const row = y * W;
        const topRow = (y > 0 ? y - 1 : 0) * W;
        const botRow = (y < H - 1 ? y + 1 : H - 1) * W;

        for (let x = 0; x < W; x++) {
          const idx = row + x;
          const center = heatGrid[idx];

          if (center <= 0.002) {
            nextGrid[idx] = 0;
            continue;
          }

          const left = heatGrid[row + (x > 0 ? x - 1 : 0)];
          const right = heatGrid[row + (x < W - 1 ? x + 1 : W - 1)];
          const top = heatGrid[topRow + x];
          const bot = heatGrid[botRow + x];

          // 3x3 mild diffusion
          const diffused = center * (1 - 4 * diff) + (left + right + top + bot) * diff;
          // Cooling decay
          const cooled = Math.max(0, diffused - decay);

          if (cooled < 0.0025) {
            nextGrid[idx] = 0;
          } else {
            nextGrid[idx] = cooled;
            if (cooled > maxHeat) {
              maxHeat = cooled;
            }
          }
        }
      }

      // Swap buffer references
      const tmp = heatGrid;
      heatGrid = nextGrid;
      nextGrid = tmp;

      // Render cells to 32-bit packed color buffer via LUT
      for (let i = 0; i < totalCells; i++) {
        const h = heatGrid[i];
        if (h <= 0.001) {
          data32[i] = 0; // fully transparent
        } else {
          const lutIdx = Math.min(255, (h * 255) | 0);
          data32[i] = LUT_32[lutIdx];
        }
      }

      ctx.putImageData(imgData, 0, 0);

      // When everything cools down completely, pause RAF loop
      if (maxHeat <= 0.0025) {
        hasHeat = false;
        isRunning = false;
        ctx.clearRect(0, 0, W, H);
        return;
      }

      animFrameId = requestAnimationFrame(loop);
    };

    const startLoop = () => {
      if (!isRunning) {
        isRunning = true;
        prevFrameTime = performance.now();
        animFrameId = requestAnimationFrame(loop);
      }
    };

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && hasHeat) {
        startLoop();
      }
    };

    window.addEventListener('pointermove', handlePointerMove, { passive: true });
    window.addEventListener('pointerdown', handlePointerDown, { passive: true });
    window.addEventListener('pointerleave', handlePointerLeave, { passive: true });
    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerdown', handlePointerDown);
      window.removeEventListener('pointerleave', handlePointerLeave);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      cancelAnimationFrame(animFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 w-full h-full pointer-events-none z-[2]"
      style={{
        mixBlendMode: 'screen',
        imageRendering: 'auto',
      }}
    />
  );
};
