import { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { motion, useScroll, useTransform, useMotionValueEvent } from 'framer-motion';
import { User, Lock, ArrowRight } from 'lucide-react';
import StarField from '../components/StarField';
import LiquidCard from '../components/LiquidCard';

const Login = () => {
  const { scrollYProgress } = useScroll();
  // Scroll animations for hero text
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 0.3], [0, -50]);
  
  // Scroll animations for login card
  const cardOpacity = useTransform(scrollYProgress, [0.4, 0.8], [0, 1]);
  const cardY = useTransform(scrollYProgress, [0.4, 0.8], [50, 0]);

  const cardPointerEvents = useTransform(scrollYProgress, [0.4, 0.5], ["none", "auto"]);
  const cardVisibility = useTransform(scrollYProgress, [0.4, 0.5], ["hidden", "visible"]);

  const formRef = useRef<HTMLFormElement>(null);

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    if (latest < 0.3 && formRef.current) {
      const activeElement = document.activeElement as HTMLElement;
      if (formRef.current.contains(activeElement)) {
        activeElement.blur();
      }
    }
  });

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login attempt');
    // Auth logic will go here
  };

  return (
    <div className="h-[200vh] w-full bg-black relative text-white selection:bg-ember-500/30">
      
      {/* Fixed WebGL Background */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 100], fov: 60 }}>
          <StarField />
        </Canvas>
        {/* Vignette overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)] pointer-events-none" />
      </div>

      {/* Hero Section */}
      <motion.div 
        style={{ opacity: heroOpacity, y: heroY }}
        className="fixed inset-0 z-10 flex flex-col items-center justify-center pointer-events-none px-6 text-center"
      >
        <h1 className="text-5xl md:text-7xl tracking-tighter mb-4 inline-block pr-2">
          <span className="font-[250]">Fire</span> <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-ember-400 to-ember-600">Watcher</span>
        </h1>
      </motion.div>

      {/* Login Card Section */}
      <div className="absolute bottom-0 w-full h-[100vh] flex items-center justify-center p-6 z-20 pointer-events-none">
        <motion.div 
          style={{ opacity: cardOpacity, y: cardY, pointerEvents: cardPointerEvents as any, visibility: cardVisibility as any }}
          className="w-full max-w-md"
        >
          <LiquidCard>
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold mb-2">Acesso Restrito</h2>
              <p className="text-white/50 text-sm">Insira suas credenciais para monitorar as áreas de risco.</p>
            </div>

            <form ref={formRef} onSubmit={handleLogin} className="space-y-5">
              <div className="space-y-1">
                <label className="text-xs text-white/70 uppercase tracking-wider ml-1">Usuário</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-white/40 group-focus-within:text-ember-400 transition-colors" />
                  </div>
                  <input
                    type="text"
                    className="block w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-ember-500/50 focus:border-ember-500/50 transition-all backdrop-blur-sm shadow-[inset_0_1px_2px_rgba(0,0,0,0.4)] focus:scale-[1.01]"
                    placeholder="Digite seu usuário"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs text-white/70 uppercase tracking-wider ml-1">Senha de Acesso</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-white/40 group-focus-within:text-ember-400 transition-colors" />
                  </div>
                  <input
                    type="password"
                    className="block w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-ember-500/50 focus:border-ember-500/50 transition-all backdrop-blur-sm shadow-[inset_0_1px_2px_rgba(0,0,0,0.4)] focus:scale-[1.01]"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm mt-2">
                <label className="flex items-center space-x-2 cursor-pointer group">
                  <input type="checkbox" className="rounded border-white/20 bg-white/5 text-ember-500 focus:ring-ember-500/50 focus:ring-offset-0" />
                  <span className="text-white/60 group-hover:text-white/90 transition-colors">Lembrar dispositivo</span>
                </label>
                <a href="#" className="text-ember-400 hover:text-ember-300 transition-colors">Esqueceu a senha?</a>
              </div>

              <button
                type="submit"
                className="relative overflow-hidden w-full mt-6 bg-gradient-to-r from-[rgba(255,110,40,0.55)] to-[rgba(255,60,20,0.8)] hover:from-[rgba(255,120,50,0.65)] hover:to-[rgba(255,70,30,0.9)] text-white font-medium py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all transform hover:scale-[1.01] active:scale-[0.97] shadow-[0_0_20px_rgba(230,74,25,0.4)] backdrop-blur-md border border-white/20 before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-white/50 before:to-transparent"
              >
                <span className="relative z-10">Autenticar</span>
                <ArrowRight className="w-5 h-5 relative z-10" />
              </button>
            </form>
          </LiquidCard>
        </motion.div>
      </div>

    </div>
  );
};

export default Login;
