/**
 * Galaxy Engine — WebGL Cosmic Background (Three.js)
 * Renderiza uma galáxia espiral viva com partículas, shaders aditivos,
 * núcleo luminoso e brasas em órbita com resposta a scroll e paralaxe do mouse.
 */

import * as THREE from 'three';

export class GalaxyBackground {
    constructor(canvasId = 'galaxy-canvas') {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas com ID '${canvasId}' não encontrado.`);
            return;
        }

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.galaxyPoints = null;
        this.starfieldPoints = null;
        this.material = null;

        // Controle de Animação e Estados
        this.clock = new THREE.Clock();
        this.animationFrameId = null;
        this.isTabActive = true;
        this.scrollProgress = 0.0;
        this.targetScrollProgress = 0.0;

        // Paralaxe do Mouse com Amortecimento (Lerp)
        this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };

        // Parâmetros da Galáxia
        this.params = {
            particleCount: 95000,
            starfieldCount: 3500,
            arms: 3,
            radius: 12.0,
            spin: 0.85,
            power: 3.5,
            baseSize: 22.0,
            cameraBaseZ: 17.5,
            cameraZoomZ: 11.5,
            baseSpeed: 0.045,
            activeSpeed: 0.09
        };

        this.init();
    }

    init() {
        try {
            this.setupRenderer();
            this.setupScene();
            this.setupCamera();
            this.createGalaxy();
            this.createStarfield();
            this.bindEvents();
            this.animate();
        } catch (error) {
            console.warn("WebGL não suportado ou falhou na inicialização. Ativando fallback Canvas 2D.", error);
            this.init2DFallback();
        }
    }

    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.renderer.setPixelRatio(dpr);
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x02030a, 1.0);
    }

    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x02030a, 0.025);
    }

    setupCamera() {
        const aspect = window.innerWidth / window.innerHeight;
        this.camera = new THREE.PerspectiveCamera(55, aspect, 0.1, 100);
        this.camera.position.set(0, 7.5, this.params.cameraBaseZ);
        this.camera.lookAt(0, 0, 0);
    }

    createGalaxy() {
        const { particleCount, arms, radius, spin, power } = this.params;

        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const aScale = new Float32Array(particleCount);
        const aRandomness = new Float32Array(particleCount);
        const aTwinkleSpeed = new Float32Array(particleCount);

        // Paleta de Cores Espectrais e Fogo
        const colorCore = new THREE.Color(0xf0f9ff);        // Branco com nuance ciano brilhante
        const colorInnerArm = new THREE.Color(0xfb923c);    // Âmbar / Laranja fogo
        const colorCrimson = new THREE.Color(0xdc2626);     // Vermelho carmesim
        const colorDeepRed = new THREE.Color(0x881337);     // Vinho / Brasa profunda
        const colorEmber = new THREE.Color(0xff4500);       // Brasa intensa

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;

            // Distribuição de raio (concentrada no núcleo luminoso)
            const rRandom = Math.random();
            const r = Math.pow(rRandom, power) * radius;

            // Distribuição nos braços espirais
            const armAngle = ((i % arms) * (Math.PI * 2)) / arms;
            const spinAngle = r * spin;

            // Dispersão aleatória progressiva com a distância
            const spreadFactor = Math.pow(r / radius, 1.25);
            const randomX = (Math.pow(Math.random(), 2.0) * (Math.random() < 0.5 ? 1 : -1) * 0.75 + (Math.random() - 0.5) * 0.4) * spreadFactor;
            const randomY = (Math.pow(Math.random(), 2.0) * (Math.random() < 0.5 ? 1 : -1) * 0.35 + (Math.random() - 0.5) * 0.25) * spreadFactor;
            const randomZ = (Math.pow(Math.random(), 2.0) * (Math.random() < 0.5 ? 1 : -1) * 0.75 + (Math.random() - 0.5) * 0.4) * spreadFactor;

            positions[i3] = Math.cos(armAngle + spinAngle) * r + randomX;
            positions[i3 + 1] = randomY * 1.5;
            positions[i3 + 2] = Math.sin(armAngle + spinAngle) * r + randomZ;

            // Interpolação de cor em função da proximidade ao núcleo
            const normR = r / radius;
            const mixedColor = colorCore.clone();

            if (normR < 0.22) {
                // Núcleo branco-azulado denso
                mixedColor.lerp(colorInnerArm, normR / 0.22);
            } else if (normR < 0.65) {
                // Transição para âmbar e vermelho queimada
                const t = (normR - 0.22) / (0.65 - 0.22);
                mixedColor.copy(colorInnerArm).lerp(colorCrimson, t);
            } else {
                // Braços externos carmesim e brasa
                const t = (normR - 0.65) / (1.0 - 0.65);
                mixedColor.copy(colorCrimson).lerp(colorDeepRed, t);
            }

            // Inserção esparsa de brasas incandescentes
            if (Math.random() < 0.08) {
                mixedColor.copy(colorEmber);
            }

            colors[i3] = mixedColor.r;
            colors[i3 + 1] = mixedColor.g;
            colors[i3 + 2] = mixedColor.b;

            // Escala e parâmetros de cintilação
            aScale[i] = (Math.random() * 0.8 + 0.3) * (1.0 - normR * 0.4);
            aRandomness[i] = Math.random() * Math.PI * 2;
            aTwinkleSpeed[i] = Math.random() * 3.0 + 1.0;
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('aScale', new THREE.BufferAttribute(aScale, 1));
        geometry.setAttribute('aRandomness', new THREE.BufferAttribute(aRandomness, 1));
        geometry.setAttribute('aTwinkleSpeed', new THREE.BufferAttribute(aTwinkleSpeed, 1));

        // Vertex Shader Customizado com atenuação de perspectiva e cintilação
        const vertexShader = `
            uniform float uTime;
            uniform float uSize;
            uniform float uPixelRatio;
            uniform float uScrollProgress;

            attribute float aScale;
            attribute float aRandomness;
            attribute float aTwinkleSpeed;

            varying vec3 vColor;
            varying float vAlpha;

            void main() {
                vColor = color;

                vec4 modelPosition = modelMatrix * vec4(position, 1.0);
                vec4 viewPosition = viewMatrix * modelPosition;
                vec4 projectedPosition = projectionMatrix * viewPosition;

                gl_Position = projectedPosition;

                // Modulação de tamanho por distância e cintilação sinusoidal
                float twinkle = 0.75 + 0.35 * sin(uTime * aTwinkleSpeed + aRandomness);
                float sizeAttenuation = 1.0 / -viewPosition.z;

                gl_PointSize = uSize * aScale * uPixelRatio * sizeAttenuation * twinkle;
                
                // Atenuação de opacidade com a profundidade
                vAlpha = smoothstep(30.0, 5.0, -viewPosition.z);
            }
        `;

        // Fragment Shader Circular com decaimento exponencial suave (Additive Glow)
        const fragmentShader = `
            varying vec3 vColor;
            varying float vAlpha;

            void main() {
                // Cálculo de distância do centro do ponto (0.0 no centro, 0.5 na borda)
                float dist = length(gl_PointCoord - vec2(0.5));
                if (dist > 0.5) discard;

                // Decaimento radial suave (glow exponencial)
                float strength = pow(1.0 - (dist * 2.0), 2.2);
                float core = exp(-dist * 9.0);

                vec3 finalColor = vColor + vec3(core * 0.45);
                gl_FragColor = vec4(finalColor, strength * vAlpha);
            }
        `;

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.material = new THREE.ShaderMaterial({
            vertexShader,
            fragmentShader,
            uniforms: {
                uTime: { value: 0 },
                uSize: { value: this.params.baseSize },
                uPixelRatio: { value: dpr },
                uScrollProgress: { value: 0 }
            },
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            transparent: true,
            vertexColors: true
        });

        this.galaxyPoints = new THREE.Points(geometry, this.material);
        this.galaxyPoints.rotation.x = THREE.MathUtils.degToRad(58); // Inclinação angular da galáxia
        this.scene.add(this.galaxyPoints);
    }

    createStarfield() {
        const count = this.params.starfieldCount;
        const positions = new Float32Array(count * 3);
        const colors = new Float32Array(count * 3);

        const starColor = new THREE.Color(0xa5f3fc);

        for (let i = 0; i < count; i++) {
            const i3 = i * 3;
            const r = 25.0 + Math.random() * 35.0;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos((Math.random() * 2) - 1);

            positions[i3] = r * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = r * Math.cos(phi);

            const c = starColor.clone().multiplyScalar(Math.random() * 0.6 + 0.3);
            colors[i3] = c.r;
            colors[i3 + 1] = c.g;
            colors[i3 + 2] = c.b;
        }

        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const material = new THREE.PointsMaterial({
            size: 1.2,
            vertexColors: true,
            transparent: true,
            opacity: 0.55,
            blending: THREE.AdditiveBlending
        });

        this.starfieldPoints = new THREE.Points(geometry, material);
        this.scene.add(this.starfieldPoints);
    }

    bindEvents() {
        window.addEventListener('resize', this.onResize.bind(this));

        // Rastreamento de paralaxe do mouse
        window.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth) * 2 - 1;
            const y = -(e.clientY / window.innerHeight) * 2 + 1;
            this.mouse.targetX = x * 0.45;
            this.mouse.targetY = y * 0.45;
        });

        // Pausar renderizador em segundo plano para economia de energia/GPU
        document.addEventListener('visibilitychange', () => {
            this.isTabActive = !document.hidden;
            if (this.isTabActive) {
                this.clock.start();
                this.animate();
            } else {
                cancelAnimationFrame(this.animationFrameId);
            }
        });
    }

    onResize() {
        if (!this.camera || !this.renderer) return;

        const width = window.innerWidth;
        const height = window.innerHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.renderer.setPixelRatio(dpr);
        this.renderer.setSize(width, height);

        if (this.material) {
            this.material.uniforms.uPixelRatio.value = dpr;
        }
    }

    setScrollProgress(progress) {
        this.targetScrollProgress = THREE.MathUtils.clamp(progress, 0, 1);
    }

    animate() {
        if (!this.isTabActive) return;

        this.animationFrameId = requestAnimationFrame(this.animate.bind(this));

        const elapsedTime = this.clock.getElapsedTime();

        // Amortecimento do scroll progress (lerp suave)
        this.scrollProgress += (this.targetScrollProgress - this.scrollProgress) * 0.08;

        // Amortecimento do paralaxe do mouse
        this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
        this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;

        // Atualização dos uniforms
        if (this.material) {
            this.material.uniforms.uTime.value = elapsedTime;
            this.material.uniforms.uScrollProgress.value = this.scrollProgress;
        }

        // Rotação da galáxia (acelera sutilmente com o scroll)
        const currentSpeed = THREE.MathUtils.lerp(
            this.params.baseSpeed,
            this.params.activeSpeed,
            this.scrollProgress
        );

        if (this.galaxyPoints) {
            this.galaxyPoints.rotation.z = elapsedTime * currentSpeed;
            // Efeito de oscilação suave
            this.galaxyPoints.rotation.y = this.mouse.x * 0.15;
            this.galaxyPoints.rotation.x = THREE.MathUtils.degToRad(58) + (this.mouse.y * 0.15);
        }

        // Rotação do campo estelar de fundo (paralaxe profundo)
        if (this.starfieldPoints) {
            this.starfieldPoints.rotation.y = elapsedTime * 0.008 + (this.mouse.x * 0.05);
            this.starfieldPoints.rotation.x = this.mouse.y * 0.05;
        }

        // Zoom suave da câmera orientado pelo scroll (progress 0 -> 1)
        const targetCamZ = THREE.MathUtils.lerp(
            this.params.cameraBaseZ,
            this.params.cameraZoomZ,
            this.scrollProgress
        );
        const targetCamY = THREE.MathUtils.lerp(7.5, 4.0, this.scrollProgress);

        this.camera.position.z = targetCamZ;
        this.camera.position.y = targetCamY;
        this.camera.position.x = this.mouse.x * 0.8;
        this.camera.lookAt(0, 0, 0);

        this.renderer.render(this.scene, this.camera);
    }

    init2DFallback() {
        const ctx = this.canvas.getContext('2d');
        if (!ctx) return;

        let width = (this.canvas.width = window.innerWidth);
        let height = (this.canvas.height = window.innerHeight);

        const stars = Array.from({ length: 400 }, () => ({
            x: Math.random() * width,
            y: Math.random() * height,
            radius: Math.random() * 1.5,
            alpha: Math.random() * 0.8 + 0.2,
            speed: Math.random() * 0.4 + 0.1
        }));

        const render2D = () => {
            ctx.fillStyle = '#02030a';
            ctx.fillRect(0, 0, width, height);

            // Núcleo radial gradiente
            const grad = ctx.createRadialGradient(
                width / 2, height / 2, 10,
                width / 2, height / 2, Math.min(width, height) * 0.6
            );
            grad.addColorStop(0, 'rgba(56, 189, 248, 0.25)');
            grad.addColorStop(0.3, 'rgba(234, 88, 12, 0.18)');
            grad.addColorStop(0.8, 'rgba(220, 38, 38, 0.05)');
            grad.addColorStop(1, 'transparent');

            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, width, height);

            ctx.fillStyle = '#ffffff';
            for (const star of stars) {
                ctx.globalAlpha = star.alpha;
                ctx.beginPath();
                ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
                ctx.fill();
                star.y += star.speed;
                if (star.y > height) star.y = 0;
            }
            ctx.globalAlpha = 1.0;

            requestAnimationFrame(render2D);
        };

        render2D();
    }
}
