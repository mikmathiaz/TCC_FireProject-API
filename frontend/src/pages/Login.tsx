import { useState } from 'react';
import { Eye } from 'lucide-react';
import { motion } from 'framer-motion';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login attempt:', { email, rememberMe });
  };

  return (
    <div className="min-h-screen w-full bg-[#050713] text-white flex items-center justify-center relative overflow-hidden font-sans select-none antialiased px-4 py-8 sm:px-6 lg:px-12">
      {/* Animated Deep Thermal Infrared Orbs (Cold Blue, Vivid Purple, Lime Green, Fiery Red) */}
      
      {/* Orb 1: Strong Cobalt Blue & Violet (Top-Left) */}
      <motion.div 
        animate={{
          x: [0, 90, -50, 0],
          y: [0, -60, 45, 0],
          scale: [1, 1.08, 0.95, 1],
        }}
        transition={{
          duration: 22,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -top-[15%] -left-[10%] w-[880px] h-[880px] rounded-full pointer-events-none opacity-55 blur-[140px]"
        style={{
          background: 'radial-gradient(circle, rgba(0, 85, 255, 0.7) 0%, rgba(124, 58, 237, 0.5) 45%, transparent 75%)'
        }}
      />

      {/* Orb 2: Hot Infrared Red, Orange & Solar Yellow (Bottom-Right) */}
      <motion.div 
        animate={{
          x: [0, -80, 60, 0],
          y: [0, 60, -45, 0],
          scale: [1, 0.93, 1.07, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -bottom-[20%] -right-[5%] w-[860px] h-[860px] rounded-full pointer-events-none opacity-45 blur-[150px]"
        style={{
          background: 'radial-gradient(circle, rgba(255, 0, 56, 0.65) 0%, rgba(255, 110, 0, 0.45) 40%, rgba(255, 220, 0, 0.25) 65%, transparent 80%)'
        }}
      />

      {/* Orb 3: Thermal Green & Cyan Transition Wave (Center / Left) */}
      <motion.div 
        animate={{
          x: [0, 60, -70, 0],
          y: [0, 45, -55, 0],
          scale: [0.95, 1.06, 0.98, 0.95],
        }}
        transition={{
          duration: 19,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-[25%] left-[25%] w-[760px] h-[760px] rounded-full pointer-events-none opacity-30 blur-[135px]"
        style={{
          background: 'radial-gradient(circle, rgba(0, 230, 64, 0.45) 0%, rgba(0, 180, 255, 0.3) 50%, transparent 75%)'
        }}
      />

      {/* Orb 4: Deep Thermal Purple & Magenta Glow (Top-Right Behind Card) */}
      <motion.div 
        animate={{
          x: [0, -50, 70, 0],
          y: [0, -35, 45, 0],
          scale: [1, 1.05, 0.94, 1],
        }}
        transition={{
          duration: 24,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-[10%] right-[15%] w-[720px] h-[720px] rounded-full pointer-events-none opacity-40 blur-[140px]"
        style={{
          background: 'radial-gradient(circle, rgba(147, 51, 234, 0.6) 0%, rgba(219, 39, 119, 0.35) 45%, transparent 75%)'
        }}
      />

      {/* Main container */}
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center relative z-10 my-auto">
        
        {/* Left Column - Branding & Info */}
        <div className="lg:col-span-7 flex flex-col justify-center max-w-xl mx-auto lg:mx-0">
          
          {/* Logo + Brand name */}
          <div className="flex items-center gap-3.5 mb-10 sm:mb-12">
            <div className="w-11 h-11 rounded-2xl bg-[#131130] border border-purple-500/40 flex items-center justify-center shadow-[0_0_20px_rgba(124,58,237,0.35)]">
              <Eye className="w-5 h-5 text-[#38bdf8]" />
            </div>
            <div className="flex flex-col">
              <span className="text-white font-bold text-base tracking-tight leading-snug">Fire Watcher</span>
              <span className="text-indigo-200/70 text-xs font-normal">Monitoramento de focos de incêndio</span>
            </div>
          </div>

          {/* Heading with the True Thermal Rainbow Palette (Azul Forte -> Roxo -> Verde Forte -> Amarelo Forte -> Vermelho Forte) */}
          <h1 className="text-4xl sm:text-5xl lg:text-[3.25rem] font-bold tracking-tight leading-[1.15] mb-5">
            <span className="text-white block">Proteção ambiental,</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-[#0055ff] via-[#7c3aed] via-[#00e600] via-[#ffea00] to-[#ff0038]">
              com visão computacional.
            </span>
          </h1>

          {/* Description */}
          <p className="text-slate-300/80 text-sm sm:text-base leading-relaxed mb-10 max-w-lg font-normal">
            Fire Watcher tem como objetivo monitorar em tempo real áreas de preservação, identificando focos e emitindo alertas.
          </p>

          {/* Status / Feature Cards */}
          <div className="space-y-3.5 w-full max-w-md">
            
            {/* Feature 1 - Cold/Normal Thermal Zone (Strong Blue/Indigo) */}
            <div className="rounded-2xl bg-[#0c122b]/85 border border-indigo-500/30 px-5 py-4 backdrop-blur-xl shadow-lg shadow-blue-950/30 transition-all hover:border-indigo-400/50 hover:shadow-indigo-500/20">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#38bdf8] shadow-[0_0_12px_#38bdf8]" />
                <span className="text-white text-sm font-semibold tracking-tight">Modelo de Machine Learning</span>
              </div>
              <p className="text-indigo-200/60 text-xs mt-1 pl-[20px]">
                2 modelos treinados pro foco
              </p>
            </div>

            {/* Feature 2 - Hotspot Zone (Thermal Purple to Hot Red) */}
            <div className="rounded-2xl bg-[#120f2e]/85 border border-purple-500/30 px-5 py-4 backdrop-blur-xl shadow-lg shadow-purple-950/30 transition-all hover:border-purple-400/50 hover:shadow-purple-500/20">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#ec4899] shadow-[0_0_12px_#ec4899]" />
                <span className="text-white text-sm font-semibold tracking-tight">Alertas em Tempo Real</span>
              </div>
              <p className="text-purple-200/60 text-xs mt-1 pl-[20px]">
                com métricas especializadas
              </p>
            </div>

          </div>
        </div>

        {/* Right Column - Login Card */}
        <div className="lg:col-span-5 w-full flex justify-center lg:justify-end">
          <div className="w-full max-w-[460px] rounded-[28px] bg-[#0c1026]/90 backdrop-blur-2xl border border-indigo-500/25 p-7 sm:p-9 shadow-[0_32px_64px_-16px_rgba(2,6,23,0.85),inset_0_1px_0_rgba(168,85,247,0.25)]">
            
            {/* Card Header */}
            <div className="mb-6">
              <h2 className="text-2xl sm:text-[1.65rem] font-bold text-white tracking-tight mb-1">
                Bem-vindo de volta
              </h2>
              <p className="text-indigo-200/70 text-sm">
                Acesse seu painel
              </p>
            </div>

            {/* Social Logins */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              
              {/* Google Button */}
              <button
                type="button"
                className="h-11 rounded-xl bg-[#131a38]/90 hover:bg-[#1a234d] border border-indigo-500/20 text-slate-200 text-sm font-medium flex items-center justify-center gap-2.5 transition-all shadow-sm active:scale-[0.98]"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path
                    fill="#EA4335"
                    d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.9C6.2 7.1 8.8 5 12 5z"
                  />
                  <path
                    fill="#4285F4"
                    d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.6h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.9z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.3 14.7c-.2-.7-.4-1.5-.4-2.7s.2-2 .4-2.7L1.6 6.4C.6 8.3 0 10.1 0 12s.6 3.7 1.6 5.6l3.7-2.9z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.2 0-5.8-2.1-6.7-5.3L1.6 16c1.9 3.8 5.8 7 10.4 7z"
                  />
                </svg>
                <span>Google</span>
              </button>

              {/* GitHub Button */}
              <button
                type="button"
                className="h-11 rounded-xl bg-[#131a38]/90 hover:bg-[#1a234d] border border-indigo-500/20 text-slate-200 text-sm font-medium flex items-center justify-center gap-2.5 transition-all shadow-sm active:scale-[0.98]"
              >
                <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                <span>GitHub</span>
              </button>

            </div>

            {/* Divider */}
            <div className="relative my-6 flex items-center justify-center">
              <div className="border-t border-indigo-500/25 w-full" />
              <span className="absolute bg-[#0c1026] px-3 text-[10px] sm:text-[11px] font-semibold tracking-wider text-indigo-300/70 uppercase">
                OU COM E-MAIL
              </span>
            </div>

            {/* Form */}
            <form onSubmit={handleLogin} className="space-y-4">
              
              {/* E-mail */}
              <div>
                <label className="text-xs font-medium text-indigo-200/80 mb-1.5 block">
                  E-mail
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="seu@email.com"
                  className="w-full h-11 px-4 bg-[#12193b]/80 border border-indigo-500/30 rounded-xl text-white text-sm placeholder-indigo-300/40 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 transition-all"
                />
              </div>

              {/* Password */}
              <div>
                <label className="text-xs font-medium text-indigo-200/80 mb-1.5 block">
                  Senha
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full h-11 px-4 bg-[#12193b]/80 border border-indigo-500/30 rounded-xl text-white text-sm placeholder-indigo-300/40 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400/50 transition-all tracking-widest"
                />
              </div>

              {/* Keep connected & Forgot password */}
              <div className="flex items-center justify-between pt-1 pb-2 text-xs sm:text-sm">
                <label className="flex items-center cursor-pointer select-none group">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-indigo-500/40 bg-indigo-950/80 text-purple-500 focus:ring-0 focus:ring-offset-0 cursor-pointer accent-purple-500"
                  />
                  <span className="text-indigo-200/70 group-hover:text-indigo-200 ml-2 transition-colors">
                    Manter conectado
                  </span>
                </label>
                <a
                  href="#"
                  className="text-purple-400 hover:text-purple-300 transition-colors"
                >
                  Esqueci a senha
                </a>
              </div>

              {/* Submit Button with the Complete Thermal Spectrum (Strong Blue -> Purple -> Magenta -> Orange -> Yellow) */}
              <button
                type="submit"
                className="w-full h-12 rounded-xl font-bold text-sm sm:text-base text-white bg-gradient-to-r from-[#2563eb] via-[#7c3aed] via-[#db2777] via-[#ea580c] to-[#facc15] hover:opacity-95 hover:shadow-[0_0_30px_rgba(124,58,237,0.45)] active:scale-[0.99] transition-all duration-200 flex items-center justify-center cursor-pointer"
              >
                Entrar no painel
              </button>

            </form>

            {/* Card Footer */}
            <div className="mt-6 text-center text-xs sm:text-sm text-slate-400">
              <span>Novo por aqui? </span>
              <a href="#" className="text-purple-400 hover:text-purple-300 font-medium hover:underline ml-0.5">
                Criar conta
              </a>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};

export default Login;
