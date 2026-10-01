import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const StarField = ({ scrollProgress = 0 }: { scrollProgress?: number }) => {
  const pointsRef = useRef<THREE.Points>(null);
  
  // Create 15k particles
  const count = 15000;
  
  const [positions, sizes, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const size = new Float32Array(count);
    const color = new Float32Array(count * 3);
    
    const colorPalette = [
      new THREE.Color('#3a0d0d'), // Dark ember
      new THREE.Color('#731a1a'), // Medium ember
      new THREE.Color('#a62626'), // Bright red
      new THREE.Color('#e64a19'), // Orange
      new THREE.Color('#ff7043'), // Light orange
    ];
    
    for (let i = 0; i < count; i++) {
      // Spherical distribution
      const r = 50 + Math.random() * 150;
      const theta = 2 * Math.PI * Math.random();
      const phi = Math.acos(2 * Math.random() - 1);
      
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
      
      size[i] = Math.random() * 2.0;
      
      const c = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      color[i * 3] = c.r;
      color[i * 3 + 1] = c.g;
      color[i * 3 + 2] = c.b;
    }
    return [pos, size, color];
  }, [count]);
  
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uScroll: { value: 0 }
  }), []);

  useFrame((state) => {
    if (pointsRef.current) {
      // Slowly rotate the entire system
      pointsRef.current.rotation.y = state.clock.elapsedTime * 0.02 + scrollProgress * 0.5;
      pointsRef.current.rotation.x = state.clock.elapsedTime * 0.01;
      
      // Update shader uniforms
      const material = pointsRef.current.material as THREE.ShaderMaterial;
      material.uniforms.uTime.value = state.clock.elapsedTime;
      material.uniforms.uScroll.value = scrollProgress;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-size"
          count={count}
          array={sizes}
          itemSize={1}
        />
        <bufferAttribute
          attach="attributes-color"
          count={count}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <shaderMaterial
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        uniforms={uniforms}
        vertexShader={`
          attribute float size;
          attribute vec3 color;
          varying vec3 vColor;
          uniform float uTime;
          uniform float uScroll;
          
          void main() {
            vColor = color;
            // Add some subtle pulsating based on time and scroll
            vec3 pos = position;
            pos.y += sin(uTime + pos.x) * 2.0;
            pos.z += cos(uTime + pos.y) * 2.0;
            
            // Push stars forward when scrolling
            pos.z += uScroll * 100.0;
            
            vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
            gl_PointSize = size * (300.0 / -mvPosition.z) * (1.0 + uScroll);
            gl_Position = projectionMatrix * mvPosition;
          }
        `}
        fragmentShader={`
          varying vec3 vColor;
          void main() {
            // Circular particle
            float dist = distance(gl_PointCoord, vec2(0.5));
            if (dist > 0.5) discard;
            
            // Soft edges
            float alpha = smoothstep(0.5, 0.1, dist);
            gl_FragColor = vec4(vColor, alpha * 0.8);
          }
        `}
      />
    </points>
  );
};

export default StarField;
