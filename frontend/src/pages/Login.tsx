import { useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Flame, Lock, Mail, ArrowRight } from 'lucide-react';
import StarField from '../components/StarField';
import LiquidCard from '../components/LiquidCard';
import { useScrollProgress } from '../hooks/useScrollProgress';

const Login = () => {
  const { scrollYProgress } = useScroll();
  const rawScrollProgress = useScrollProgress();

  // Scroll animations for hero text
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  const heroY = useTransform(scrollYProgress, [0, 0.3], [0, -50]);
  
  // Scroll animations for login card
  const cardOpacity = useTransform(scrollYProgress, [0.4, 0.8], [0, 1]);
  const cardY = useTransform(scrollYProgress, [0.4, 0.8], [50, 0]);

  // Lock scroll after card is fully visible to prevent scrolling past it
  useEffect(() => {
    if (rawScrollProgress >= 1) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }
  }, [rawScrollProgress]);

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
          <StarField scrollProgress={rawScrollProgress} />
        </Canvas>
        {/* Vignette overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)] pointer-events-none" />
      </div>

      {/* Hero Section */}
      <motion.div 
        style={{ opacity: heroOpacity, y: heroY }}
        className="fixed inset-0 z-10 flex flex-col items-center justify-center pointer-events-none px-6 text-center"
      >
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            <Flame className="w-16 h-16 text-ember-500 animate-pulse" />
            <div className="absolute inset-0 blur-xl bg-ember-500/30 rounded-full -z-10" />
          </div>
        </div>
        <h1 className="text-5xl md:text-7xl font-light tracking-tighter mb-4">
          Fire <span className="font-semibold text-transparent bg-clip-text bg-gradient-to-r from-ember-400 to-ember-600">Watcher</span>
        </h1>
        <p className="text-lg md:text-xl text-white/60 max-w-lg font-light">
          Sistema de Monitoramento Inteligente e Detecção Precoce de Queimadas.
        </p>
        <div className="mt-12 flex flex-col items-center opacity-50 animate-bounce">
          <p className="text-sm uppercase tracking-widest mb-2">Role para Entrar</p>
          <div className="w-[1px] h-12 bg-gradient-to-b from-white to-transparent" />
        </div>
      </motion.div>

      {/* Login Card Section */}
      <div className="absolute bottom-0 w-full h-[100vh] flex items-center justify-center p-6 z-20">
        <motion.div 
          style={{ opacity: cardOpacity, y: cardY }}
          className="w-full max-w-md"
        >
          <LiquidCard>
            <div className="text-center mb-8">
              <h2 className="text-2xl font-semibold mb-2">Acesso Restrito</h2>
              <p className="text-white/50 text-sm">Insira suas credenciais para monitorar as áreas de risco.</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-5">
              <div className="space-y-1">
                <label className="text-xs text-white/70 uppercase tracking-wider ml-1">E-mail Operacional</label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-white/40 group-focus-within:text-ember-400 transition-colors" />
                  </div>
                  <input
                    type="email"
                    className="block w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-ember-500/50 focus:border-ember-500/50 transition-all backdrop-blur-sm"
                    placeholder="operador@inpe.br"
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
                    className="block w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-ember-500/50 focus:border-ember-500/50 transition-all backdrop-blur-sm"
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
                className="w-full mt-6 bg-gradient-to-r from-ember-600 to-ember-500 hover:from-ember-500 hover:to-ember-400 text-white font-medium py-3 px-4 rounded-xl flex items-center justify-center space-x-2 transition-all transform hover:scale-[1.02] active:scale-95 shadow-[0_0_20px_rgba(230,74,25,0.4)]"
              >
                <span>Autenticar</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </form>
          </LiquidCard>
        </motion.div>
      </div>

    </div>
  );
};

export default Login;
