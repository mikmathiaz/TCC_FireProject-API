import { useRef, useMemo, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';

const MAX_PARTICLES = 10000;
const AMBIENT_COUNT = 6000;

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
    
    float age = instanceInfo.x;
    float size = instanceInfo.y;
    float seed = instanceInfo.z;
    float type = instanceInfo.w;
    
    vec3 vel = instanceVel;
    float speed = length(vel);
    vSpeed = speed;
    
    vec3 vPos = position; 
    
    // Thickness and length
    float thickness = max(0.5, size * 0.8);
    float len = max(thickness * 1.5, size * 2.0 + speed * 0.35);
    
    // 15% are tiny dots
    if (seed < 0.15) {
      len = thickness;
    }
    
    vPos.x *= thickness;
    vPos.y *= len;
    
    // Align with velocity
    vec3 up = vec3(0.0, 1.0, 0.0);
    vec3 dir = speed > 0.1 ? vel / speed : up;
    
    vec3 camDir = vec3(0.0, 0.0, 1.0); 
    vec3 right = cross(dir, camDir);
    if(length(right) < 0.01) right = vec3(1.0, 0.0, 0.0);
    right = normalize(right);
    vec3 newNormal = cross(right, dir);
    
    mat3 rot = mat3(right, dir, newNormal);
    vPos = rot * vPos;
    
    vec3 finalPos = instancePos + vPos;
    
    // Foreground particles (3%)
    if (seed > 0.97) {
       finalPos.z += 30.0;
       vPos *= 3.0;
    }

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
    
    // Gradient along length: vUv.y goes 0 to 1. Head is at vUv.y = 1
    // For dots, it's radial
    float dist = distance(vUv, vec2(0.5));
    float shape = 0.0;
    
    if (seed < 0.15) {
      // Dot
      shape = smoothstep(0.5, 0.1, dist);
    } else {
      // Streak: intense head, fading tail, transversal falloff
      float transversal = smoothstep(0.5, 0.1, abs(vUv.x - 0.5));
      float longitudinal = vUv.y; // 1 at top, 0 at bottom
      shape = transversal * longitudinal;
      shape = pow(shape, 1.5);
    }
    
    // Color over age/temperature
    // Colors: White-yellow -> Yellow -> Orange -> Red -> Dark Red -> Transparent
    vec3 cWhite = vec3(1.0, 0.95, 0.76); // #fff4c2
    vec3 cYellow = vec3(1.0, 0.83, 0.35); // #ffd45a
    vec3 cOrange = vec3(1.0, 0.54, 0.12); // #ff8a1f
    vec3 cRed = vec3(0.88, 0.16, 0.06);   // #e02a10
    vec3 cDarkRed = vec3(0.48, 0.07, 0.03); // #7a1208
    
    // Base temp determined by age (0 is hot, 1 is cold)
    float temp = min(1.0, age * 1.5 + (1.0 - vUv.y) * 0.5); 
    
    vec3 color = vec3(0.0);
    if (temp < 0.1) color = mix(cWhite, cYellow, temp / 0.1);
    else if (temp < 0.4) color = mix(cYellow, cOrange, (temp - 0.1) / 0.3);
    else if (temp < 0.7) color = mix(cOrange, cRed, (temp - 0.4) / 0.3);
    else color = mix(cRed, cDarkRed, (temp - 0.7) / 0.3);
    
    // Flicker
    float flicker = 0.8 + 0.2 * sin(seed * 100.0 + age * 20.0);
    
    float alpha = shape * (1.0 - smoothstep(0.8, 1.0, age)) * flicker;
    
    // Foreground particles are softer/blurred
    if (seed > 0.97) {
      alpha *= 0.5;
    }
    
    if (alpha < 0.01) discard;
    
    // Halo glow
    gl_FragColor = vec4(color, alpha);
  }
`;

export default function StarField() {
  const { viewport } = useThree();
  const instancedMeshRef = useRef<THREE.InstancedMesh>(null);
  const geometryRef = useRef<THREE.InstancedBufferGeometry>(null);
  


  // Arrays
  const data = useMemo(() => {
    return {
      pos: new Float32Array(MAX_PARTICLES * 3),
      vel: new Float32Array(MAX_PARTICLES * 3),
      info: new Float32Array(MAX_PARTICLES * 4), // age, size, seed, type (0=dead, 1=ambient, 2=mouse)
    };
  }, []);

  // Initialize ambient particles
  useEffect(() => {
    const w = viewport.width;
    const h = viewport.height;
    for (let i = 0; i < AMBIENT_COUNT; i++) {
      data.pos[i * 3] = (Math.random() - 0.5) * w * 1.5;
      data.pos[i * 3 + 1] = (Math.random() - 0.5) * h * 1.5;
      data.pos[i * 3 + 2] = (Math.random() - 0.5) * 50;
      
      data.vel[i * 3] = (Math.random() - 0.5) * 10;
      data.vel[i * 3 + 1] = 5 + Math.random() * 20; // Updraft
      data.vel[i * 3 + 2] = (Math.random() - 0.5) * 10;
      
      data.info[i * 4] = Math.random(); // age
      data.info[i * 4 + 1] = 0.5 + Math.random() * 2.0; // size
      data.info[i * 4 + 2] = Math.random(); // seed
      data.info[i * 4 + 3] = 1; // ambient
    }
  }, [viewport, data]);

  // Mouse Interaction State
  const mouseState = useRef({
    x: 0, y: 0, 
    vx: 0, vy: 0,
    isDown: false,
    lastTime: performance.now(),
    lastActivity: performance.now()
  });

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      const ms = mouseState.current;
      const now = performance.now();
      const dt = Math.max(1, now - ms.lastTime);
      
      // Screen to world
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
    const onMouseDown = () => { mouseState.current.isDown = true; mouseState.current.lastActivity = performance.now(); };
    const onMouseUp = () => { mouseState.current.isDown = false; mouseState.current.lastActivity = performance.now(); };

    // Click burst
    const onClick = (e: MouseEvent) => {
      const wx = ((e.clientX / window.innerWidth) * 2 - 1) * viewport.width / 2;
      const wy = (-(e.clientY / window.innerHeight) * 2 + 1) * viewport.height / 2;
      
      let spawned = 0;
      for (let i = AMBIENT_COUNT; i < MAX_PARTICLES && spawned < 40; i++) {
        if (data.info[i * 4 + 3] === 0 || data.info[i * 4] >= 1.0) {
          // Spawn
          data.pos[i * 3] = wx;
          data.pos[i * 3 + 1] = wy;
          data.pos[i * 3 + 2] = 5;
          
          const angle = Math.random() * Math.PI * 2;
          const speed = 30 + Math.random() * 80;
          data.vel[i * 3] = Math.cos(angle) * speed;
          data.vel[i * 3 + 1] = Math.sin(angle) * speed + 20; // +updraft
          data.vel[i * 3 + 2] = (Math.random() - 0.5) * 20;
          
          data.info[i * 4] = 0; // age
          data.info[i * 4 + 1] = 1.0 + Math.random() * 3.0; // size
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
    
    const w = viewport.width;
    const h = viewport.height;
    const ms = mouseState.current;
    const timeSinceActivity = performance.now() - ms.lastActivity;
    const returningToNormal = timeSinceActivity > 3000;

    let activeCount = AMBIENT_COUNT;

    // Simulate Particles
    for (let i = 0; i < MAX_PARTICLES; i++) {
      const type = data.info[i * 4 + 3];
      if (type === 0) continue; // dead

      let age = data.info[i * 4];
      const px = data.pos[i * 3];
      const py = data.pos[i * 3 + 1];
      let vx = data.vel[i * 3];
      let vy = data.vel[i * 3 + 1];

      if (type === 1) { // Ambient
        age += delta * (0.1 + Math.random() * 0.1);
        
        // Swirl interaction
        if (!returningToNormal) {
          const dx = px - ms.x;
          const dy = py - ms.y;
          const distSq = dx*dx + dy*dy;
          if (distSq < 4000) {
            const dist = Math.sqrt(distSq);
            const force = (1.0 - dist / 63.0) * 5.0; // 63 is approx sqrt(4000)
            vx += ms.vx * force * delta + (dy / dist) * force * 10;
            vy += ms.vy * force * delta - (dx / dist) * force * 10;
            // heat up
            age = Math.max(0, age - force * delta);
          }
        }

        // Return to normal (drag/damping)
        vx = THREE.MathUtils.lerp(vx, (Math.sin(state.clock.elapsedTime + i) * 5), delta * 2);
        vy = THREE.MathUtils.lerp(vy, 10 + Math.cos(state.clock.elapsedTime * 0.5 + i) * 5, delta * 2);
        
        if (age >= 1.0 || py > h/2 + 20) {
          // Respawn at bottom
          age = 0;
          data.pos[i * 3] = (Math.random() - 0.5) * w * 1.5;
          data.pos[i * 3 + 1] = -h/2 - 20 - Math.random() * 50;
          vx = (Math.random() - 0.5) * 10;
          vy = 5 + Math.random() * 20;
        }
      } else if (type === 2) { // Mouse FX
        age += delta * (0.4 + Math.random() * 0.4); // Die faster
        vy -= 20 * delta; // slight gravity
        vx *= 0.95; // drag
        vy *= 0.95;
        if (age >= 1.0) {
          data.info[i * 4 + 3] = 0; // kill
        }
        activeCount = Math.max(activeCount, i + 1);
      }

      data.pos[i * 3] += vx * delta;
      data.pos[i * 3 + 1] += vy * delta;
      data.pos[i * 3 + 2] += data.vel[i * 3 + 2] * delta;
      
      data.vel[i * 3] = vx;
      data.vel[i * 3 + 1] = vy;
      data.info[i * 4] = age;
    }

    // Drag fire spawn
    if (ms.isDown) {
      let spawned = 0;
      for (let i = AMBIENT_COUNT; i < MAX_PARTICLES && spawned < 10; i++) {
        if (data.info[i * 4 + 3] === 0 || data.info[i * 4] >= 1.0) {
          data.pos[i * 3] = ms.x + (Math.random() - 0.5) * 5;
          data.pos[i * 3 + 1] = ms.y + (Math.random() - 0.5) * 5;
          data.pos[i * 3 + 2] = 5;
          
          data.vel[i * 3] = ms.vx * 0.5 + (Math.random() - 0.5) * 20;
          data.vel[i * 3 + 1] = ms.vy * 0.5 + 20 + Math.random() * 20; // flame goes up
          data.vel[i * 3 + 2] = (Math.random() - 0.5) * 10;
          
          data.info[i * 4] = 0; 
          data.info[i * 4 + 1] = 2.0 + Math.random() * 4.0; // bigger fire particles
          data.info[i * 4 + 2] = Math.random(); 
          data.info[i * 4 + 3] = 2; 
          spawned++;
        }
      }
    }

    // Update attributes
    geometryRef.current.attributes.instancePos.needsUpdate = true;
    geometryRef.current.attributes.instanceVel.needsUpdate = true;
    geometryRef.current.attributes.instanceInfo.needsUpdate = true;
    
    if (instancedMeshRef.current) {
       instancedMeshRef.current.count = activeCount;
    }
  });

  return (
    <>
      {/* Background radial heat */}
      <mesh position={[0, -viewport.height/2, -10]}>
        <planeGeometry args={[viewport.width * 2, viewport.height]} />
        <meshBasicMaterial 
          transparent 
          opacity={0.15} 
          color="#ff3a00" 
          blending={THREE.AdditiveBlending}
          depthWrite={false}
        />
      </mesh>
      
      <instancedMesh ref={instancedMeshRef} args={[undefined, undefined, MAX_PARTICLES]} count={AMBIENT_COUNT}>
        <planeGeometry args={[1, 1]} />
        <shaderMaterial
          transparent
          depthWrite={false}
          blending={THREE.AdditiveBlending}
          vertexShader={vertexShader}
          fragmentShader={fragmentShader}
        />
        <instancedBufferGeometry ref={geometryRef} copy={new THREE.PlaneGeometry(1, 1)}>
          <instancedBufferAttribute attach="attributes-instancePos" args={[data.pos, 3]} />
          <instancedBufferAttribute attach="attributes-instanceVel" args={[data.vel, 3]} />
          <instancedBufferAttribute attach="attributes-instanceInfo" args={[data.info, 4]} />
        </instancedBufferGeometry>
      </instancedMesh>
    </>
  );
}
