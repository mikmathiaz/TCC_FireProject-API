import { useRef, useMemo, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { VISUAL_CONFIG } from '../config/visual';

const MAX_PARTICLES = VISUAL_CONFIG.PARTICLE_COUNT + 1000;
const AMBIENT_COUNT = VISUAL_CONFIG.PARTICLE_COUNT;

const vertexShader = `
  attribute vec3 instancePos;
  attribute vec3 instanceVel;
  attribute vec4 instanceInfo; // x=age(0-1), y=size, z=seed, w=type

  varying vec2 vUv;
  varying vec4 vInfo;
  varying float vSpeed;

  void main() {
    vUv = uv;
    vInfo = instanceInfo;
    
    vec3 vel = instanceVel;
    float speed = length(vel);
    vSpeed = speed;
    
    float size = instanceInfo.y;
    
    vec3 vPos = position; 
    
    // Stretch logic: very limited
    float stretch = clamp(1.0 + (speed * 0.02), 1.0, ${VISUAL_CONFIG.STREAK_MAX.toFixed(2)});
    
    vPos.x *= size;
    vPos.y *= (size * stretch);
    
    // Align with velocity if moving fast enough
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 dir = speed > 5.0 ? vel / speed : up;
    
    vec3 camDir = vec3(0.0, 0.0, 1.0); 
    vec3 right = cross(dir, camDir);
    if(length(right) < 0.01) right = vec3(1.0, 0.0, 0.0);
    right = normalize(right);
    vec3 newNormal = cross(right, dir);
    
    mat3 rot = mat3(right, dir, newNormal);
    vPos = rot * vPos;
    
    vec3 finalPos = instancePos + vPos;
    
    vec4 mvPosition = modelViewMatrix * vec4(finalPos, 1.0);
    gl_Position = projectionMatrix * mvPosition;
  }
`;

const fragmentShader = `
  varying vec2 vUv;
  varying vec4 vInfo;
  varying float vSpeed;

  void main() {
    float age = vInfo.x;
    float seed = vInfo.z;
    float type = vInfo.w;
    
    // Shape: Circular point with soft halo
    float dist = distance(vUv, vec2(0.5));
    float shape = smoothstep(0.5, 0.0, dist);
    shape = pow(shape, 1.5); // Sharp core, soft edge
    
    // Colors: 35% Red, 35% Orange, 20% Amber, 10% Warm White
    vec3 cRed = vec3(0.88, 0.16, 0.06);     // #e02a10
    vec3 cDarkRed = vec3(0.78, 0.12, 0.05); // #c8200e
    vec3 cOrange = vec3(1.0, 0.48, 0.10);   // #ff7a1a
    vec3 cAmber = vec3(1.0, 0.70, 0.28);    // #ffb347
    vec3 cWhite = vec3(1.0, 0.88, 0.69);    // #ffe2b0
    
    vec3 baseColor = vec3(0.0);
    if (seed < 0.35) {
      baseColor = mix(cRed, cDarkRed, seed / 0.35);
    } else if (seed < 0.70) {
      baseColor = cOrange;
    } else if (seed < 0.90) {
      baseColor = cAmber;
    } else {
      baseColor = cWhite;
    }
    
    // Interaction particles (type 2) can be hotter initially
    if (type == 2.0 && age < 0.2) {
       baseColor = mix(cWhite, baseColor, age / 0.2);
    }
    
    // Twinkle effect
    float twinkle = 0.7 + 0.3 * sin(seed * 100.0 + age * 30.0);
    
    // Fade in and out
    float lifeAlpha = smoothstep(0.0, 0.1, age) * (1.0 - smoothstep(0.8, 1.0, age));
    
    float alpha = shape * lifeAlpha * twinkle * ${VISUAL_CONFIG.BRIGHTNESS.toFixed(2)};
    
    if (alpha < 0.01) discard;
    
    gl_FragColor = vec4(baseColor, alpha);
  }
`;

export default function StarField() {
  const { viewport } = useThree();
  const instancedMeshRef = useRef<THREE.InstancedMesh>(null);
  const geometryRef = useRef<THREE.BufferGeometry>(null);

  const data = useMemo(() => {
    return {
      pos: new Float32Array(MAX_PARTICLES * 3),
      vel: new Float32Array(MAX_PARTICLES * 3),
      info: new Float32Array(MAX_PARTICLES * 4),
    };
  }, []);

  const getParticleSize = (seed: number) => {
    // 80% 1-1.5, 17% 2-3, 3% 3-5
    if (seed < 0.8) return VISUAL_CONFIG.SIZE_MIN + Math.random() * 0.5;
    if (seed < 0.97) return 2.0 + Math.random() * 1.0;
    return 3.0 + Math.random() * 2.0;
  };

  useEffect(() => {
    const w = viewport.width;
    const h = viewport.height;
    for (let i = 0; i < AMBIENT_COUNT; i++) {
      data.pos[i * 3] = (Math.random() - 0.5) * w * 1.2;
      data.pos[i * 3 + 1] = (Math.random() - 0.5) * h * 1.2;
      data.pos[i * 3 + 2] = (Math.random() - 0.5) * 50; // Depth
      
      data.vel[i * 3] = (Math.random() - 0.5) * VISUAL_CONFIG.DRIFT_SPEED;
      data.vel[i * 3 + 1] = VISUAL_CONFIG.DRIFT_SPEED * 0.5 + Math.random() * VISUAL_CONFIG.DRIFT_SPEED;
      data.vel[i * 3 + 2] = (Math.random() - 0.5) * VISUAL_CONFIG.DRIFT_SPEED;
      
      const seed = Math.random();
      data.info[i * 4] = Math.random(); // age
      data.info[i * 4 + 1] = getParticleSize(seed); // size
      data.info[i * 4 + 2] = seed; // seed
      data.info[i * 4 + 3] = 1; // ambient
    }
  }, [viewport, data]);

  const mouseState = useRef({
    x: 0, y: 0, 
    vx: 0, vy: 0,
    isDown: false,
    lastTime: performance.now(),
    lastActivity: performance.now()
  });

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      // Ignore if starting on card
      if ((e.target as HTMLElement).closest('.group\\/card')) return;

      const ms = mouseState.current;
      const now = performance.now();
      const dt = Math.max(1, now - ms.lastTime);
      
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1;
      const wx = x * viewport.width / 2;
      const wy = y * viewport.height / 2;
      
      ms.vx = ((wx - ms.x) / dt) * 100;
      ms.vy = ((wy - ms.y) / dt) * 100;
      ms.x = wx;
      ms.y = wy;
      ms.lastTime = now;
      ms.lastActivity = now;
    };
    
    const onMouseDown = (e: MouseEvent) => {
      if ((e.target as HTMLElement).closest('.group\\/card')) return;
      mouseState.current.isDown = true; 
      mouseState.current.lastActivity = performance.now();
    };
    
    const onMouseUp = () => { 
      mouseState.current.isDown = false; 
      mouseState.current.lastActivity = performance.now(); 
    };

    const onClick = (e: MouseEvent) => {
      if ((e.target as HTMLElement).closest('.group\\/card')) return;
      
      const wx = ((e.clientX / window.innerWidth) * 2 - 1) * viewport.width / 2;
      const wy = (-(e.clientY / window.innerHeight) * 2 + 1) * viewport.height / 2;
      
      let spawned = 0;
      for (let i = AMBIENT_COUNT; i < MAX_PARTICLES && spawned < 16; i++) {
        if (data.info[i * 4 + 3] === 0 || data.info[i * 4] >= 1.0) {
          data.pos[i * 3] = wx;
          data.pos[i * 3 + 1] = wy;
          data.pos[i * 3 + 2] = 5; // Slightly in front
          
          const angle = Math.random() * Math.PI * 2;
          // One strong spark, others tiny
          const isMain = spawned === 0;
          const speed = isMain ? 60 : 15 + Math.random() * 30;
          
          data.vel[i * 3] = Math.cos(angle) * speed;
          data.vel[i * 3 + 1] = Math.sin(angle) * speed;
          data.vel[i * 3 + 2] = (Math.random() - 0.5) * 10;
          
          data.info[i * 4] = 0; // age
          data.info[i * 4 + 1] = isMain ? 6.0 : 1.5 + Math.random(); // size
          data.info[i * 4 + 2] = Math.random(); // seed
          data.info[i * 4 + 3] = 2; // fx
          spawned++;
        }
      }
      mouseState.current.lastActivity = performance.now();
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mouseup', onMouseUp);
    window.addEventListener('click', onClick);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mouseup', onMouseUp);
      window.removeEventListener('click', onClick);
    };
  }, [viewport, data]);

  useFrame((state, delta) => {
    if (!geometryRef.current) return;
    
    // Limit delta to prevent huge jumps on tab switch
    const safeDelta = Math.min(delta, 0.05);
    
    const w = viewport.width;
    const h = viewport.height;
    const ms = mouseState.current;
    const timeSinceActivity = performance.now() - ms.lastActivity;
    const returningToNormal = timeSinceActivity > (VISUAL_CONFIG.RETURN_SECONDS * 1000);

    let activeCount = AMBIENT_COUNT;

    for (let i = 0; i < MAX_PARTICLES; i++) {
      const type = data.info[i * 4 + 3];
      if (type === 0) continue; // dead

      let age = data.info[i * 4];
      const px = data.pos[i * 3];
      const py = data.pos[i * 3 + 1];
      let vx = data.vel[i * 3];
      let vy = data.vel[i * 3 + 1];

      if (type === 1) { // Ambient
        age += safeDelta * (0.05 + Math.random() * 0.05); // Slow aging (up to 20s life)
        
        // Soft noise movement
        vx += (Math.sin(state.clock.elapsedTime * 0.5 + i) * 0.5) * safeDelta;
        
        // Hover push interaction
        if (!returningToNormal) {
          const dx = px - ms.x;
          const dy = py - ms.y;
          const distSq = dx*dx + dy*dy;
          const radiusSq = VISUAL_CONFIG.MOUSE_RADIUS * VISUAL_CONFIG.MOUSE_RADIUS;
          if (distSq < radiusSq) {
            const dist = Math.sqrt(distSq);
            const force = (1.0 - dist / VISUAL_CONFIG.MOUSE_RADIUS) * VISUAL_CONFIG.MOUSE_FORCE;
            vx += (dx / dist) * force * 10 * safeDelta;
            vy += (dy / dist) * force * 10 * safeDelta;
          }
        }

        // Return to normal drift
        vx = THREE.MathUtils.lerp(vx, (Math.sin(i) * VISUAL_CONFIG.DRIFT_SPEED), safeDelta * 2);
        vy = THREE.MathUtils.lerp(vy, VISUAL_CONFIG.DRIFT_SPEED * (0.5 + Math.random()), safeDelta * 2);
        
        if (age >= 1.0) {
          // Respawn randomly
          age = 0;
          data.pos[i * 3] = (Math.random() - 0.5) * w * 1.2;
          data.pos[i * 3 + 1] = (Math.random() - 0.5) * h * 1.2;
          vx = (Math.random() - 0.5) * VISUAL_CONFIG.DRIFT_SPEED;
          vy = VISUAL_CONFIG.DRIFT_SPEED * (0.5 + Math.random());
        }
      } else if (type === 2) { // Mouse FX (Click/Drag)
        age += safeDelta * 0.66; // 1.5s life max
        vx *= 0.92; // Drag
        vy *= 0.92;
        if (age >= 1.0) {
          data.info[i * 4 + 3] = 0; // kill
        }
        activeCount = Math.max(activeCount, i + 1);
      }

      data.pos[i * 3] += vx * safeDelta;
      data.pos[i * 3 + 1] += vy * safeDelta;
      data.pos[i * 3 + 2] += data.vel[i * 3 + 2] * safeDelta;
      
      data.vel[i * 3] = vx;
      data.vel[i * 3 + 1] = vy;
      data.info[i * 4] = age;
    }

    // Drag fire spawn
    if (ms.isDown) {
      let spawned = 0;
      for (let i = AMBIENT_COUNT; i < MAX_PARTICLES && spawned < 3; i++) {
        if (data.info[i * 4 + 3] === 0 || data.info[i * 4] >= 1.0) {
          data.pos[i * 3] = ms.x + (Math.random() - 0.5) * 4;
          data.pos[i * 3 + 1] = ms.y + (Math.random() - 0.5) * 4;
          data.pos[i * 3 + 2] = 5;
          
          data.vel[i * 3] = ms.vx * 0.2 + (Math.random() - 0.5) * 10;
          data.vel[i * 3 + 1] = ms.vy * 0.2 + (Math.random() - 0.5) * 10; 
          data.vel[i * 3 + 2] = (Math.random() - 0.5) * 5;
          
          data.info[i * 4] = 0; 
          data.info[i * 4 + 1] = 1.0 + Math.random() * 2.0; // Delicate fire
          data.info[i * 4 + 2] = Math.random(); 
          data.info[i * 4 + 3] = 2; 
          spawned++;
        }
      }
    }

    geometryRef.current.attributes.instancePos.needsUpdate = true;
    geometryRef.current.attributes.instanceVel.needsUpdate = true;
    geometryRef.current.attributes.instanceInfo.needsUpdate = true;
    
    if (instancedMeshRef.current) {
       instancedMeshRef.current.count = activeCount;
    }
  });

  return (
    <instancedMesh ref={instancedMeshRef} args={[null as any, null as any, MAX_PARTICLES]} count={AMBIENT_COUNT}>
      <planeGeometry ref={geometryRef as any} args={[1, 1]}>
        <instancedBufferAttribute attach="attributes-instancePos" args={[data.pos, 3]} />
        <instancedBufferAttribute attach="attributes-instanceVel" args={[data.vel, 3]} />
        <instancedBufferAttribute attach="attributes-instanceInfo" args={[data.info, 4]} />
      </planeGeometry>
      <shaderMaterial
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
      />
    </instancedMesh>
  );
}
