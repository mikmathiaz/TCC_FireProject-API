export const HEAT_GRID_W = 192;
export const HEAT_GRID_H = 108;
export const HEAT_RADIUS_PX = 140;
export const HEAT_COOL_SECONDS = 2.5;
export const HEAT_DIFFUSION = 0.14;
export const HEAT_CLICK_MULT = 1.6;
export const HEAT_MIN_INTENSITY = 0.35;

export const VISUAL_CONFIG = {
  // Mouse Thermal Heatmap Simulation
  HEAT_GRID_W,
  HEAT_GRID_H,
  HEAT_RADIUS_PX,
  HEAT_COOL_SECONDS,
  HEAT_DIFFUSION,
  HEAT_CLICK_MULT,
  HEAT_MIN_INTENSITY,

  // Spark Particles (legacy)
  PARTICLE_COUNT: 10000,
  SIZE_MIN: 1.0,
  SIZE_MAX: 5.0,
  HERO_SIZE_CHANCE: 0.03, // 3%
  STREAK_MAX: 1.3,
  BRIGHTNESS: 0.8,
  DRIFT_SPEED: 2.0,
  
  // Mouse Interactions
  MOUSE_RADIUS: 120.0,
  MOUSE_FORCE: 2.5,
  RETURN_SECONDS: 4.0,

  // Liquid Glass Card
  GLASS_TINT: 'rgba(8, 5, 5, 0.35)',
  GLASS_GRADIENT_START: 'rgba(255, 255, 255, 0.06)',
  GLASS_GRADIENT_END: 'rgba(255, 255, 255, 0.015)',
  GLASS_BLUR_PX: 22,
  GLASS_SATURATE: 130,
  GLASS_BRIGHTNESS: 0.75,
  GLASS_BORDER_START: 'rgba(255, 255, 255, 0.28)',
  GLASS_BORDER_END: 'rgba(255, 255, 255, 0.08)',
  GLASS_REFRACTION_SCALE: 25,
};
