import { useState } from 'react';
import { Eye } from 'lucide-react';
import { motion } from 'framer-motion';
import { ThermalMouseCanvas } from '../components/ThermalMouseCanvas';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    if (!email.trim() && !password.trim()) {
      setErrorMessage('Informe o usuário e a senha.');
      return;
    }

    setIsLoading(true);

    // Latência sutil simulada para transição elegante
    await new Promise((r) => setTimeout(r, 450));

    const result = await login(email, password, rememberMe);
    if (!result.success) {
      setIsLoading(false);
      setErrorMessage(result.error || 'Credenciais inválidas.');
    }
  };

  return (
    <div className="min-h-screen w-full bg-[#050a2e] text-white flex items-center justify-center relative overflow-hidden font-sans select-none antialiased px-4 py-8 sm:px-6 lg:px-12">
      {/* Thermal Heat Sources (Concentric Rings Thermal Ramp) */}
      
      {/* Fonte de Calor 1: Behind Login Card (Top-Right / Card Area) */}
      <motion.div 
        animate={{
          x: [0, -50, 30, 0],
          y: [0, 40, -35, 0],
          scale: [1, 1.05, 0.96, 1],
        }}
        transition={{
          duration: 55,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-[2%] -right-[6%] w-[680px] h-[680px] rounded-full pointer-events-none opacity-80 blur-[36px]"
        style={{
          background: 'radial-gradient(circle at 62% 48%, #ffffff 0%, #ff8fa8 3%, #ff2a1a 8%, #ff9a1a 14%, #f5ee28 21%, #2ee65a 29%, #12d4e8 37%, #1e6bff 47%, #0a1a8c 58%, transparent 72%)',
        }}
      />

      {/* Fonte de Calor 2: Bottom-Right Heat Core */}
      <motion.div 
        animate={{
          x: [0, 60, -40, 0],
          y: [0, -50, 30, 0],
          scale: [1, 0.94, 1.06, 1],
        }}
        transition={{
          duration: 72,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -bottom-[14%] right-[10%] w-[560px] h-[560px] rounded-full pointer-events-none opacity-75 blur-[40px]"
        style={{
          background: 'radial-gradient(circle at 45% 60%, #ffffff 0%, #ff8fa8 3%, #ff2a1a 8%, #ff9a1a 14%, #f5ee28 21%, #2ee65a 29%, #12d4e8 37%, #1e6bff 47%, #0a1a8c 58%, transparent 72%)',
        }}
      />

      {/* Fonte de Calor 3: Lower Center Transition */}
      <motion.div 
        animate={{
          x: [0, -35, 45, 0],
          y: [0, -35, 25, 0],
          scale: [0.95, 1.04, 0.98, 0.95],
        }}
        transition={{
          duration: 60,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -bottom-[8%] left-[38%] w-[440px] h-[440px] rounded-full pointer-events-none opacity-65 blur-[32px]"
        style={{
          background: 'radial-gradient(circle at 50% 50%, #ffffff 0%, #ff8fa8 3%, #ff2a1a 8%, #ff9a1a 14%, #f5ee28 21%, #2ee65a 29%, #12d4e8 37%, #1e6bff 47%, #0a1a8c 58%, transparent 72%)',
        }}
      />

      {/* Fonte de Calor 4: Distant Top-Left Halo (Core kept outside screen away from text) */}
      <motion.div 
        animate={{
          x: [0, 40, -30, 0],
          y: [0, 30, -25, 0],
          scale: [1, 1.05, 0.95, 1],
        }}
        transition={{
          duration: 82,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -top-[20%] -left-[14%] w-[540px] h-[540px] rounded-full pointer-events-none opacity-60 blur-[44px]"
        style={{
          background: 'radial-gradient(circle at 25% 25%, #ffffff 0%, #ff8fa8 3%, #ff2a1a 8%, #ff9a1a 14%, #f5ee28 21%, #2ee65a 29%, #12d4e8 37%, #1e6bff 47%, #0a1a8c 58%, transparent 72%)',
        }}
      />

      {/* Fonte de Calor 5: Top-Center Accent */}
      <motion.div 
        animate={{
          x: [0, -25, 30, 0],
          y: [0, 25, -20, 0],
          scale: [0.96, 1.04, 0.98, 0.96],
        }}
        transition={{
          duration: 48,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-[4%] left-[40%] w-[320px] h-[320px] rounded-full pointer-events-none opacity-60 blur-[28px]"
        style={{
          background: 'radial-gradient(circle at 52% 48%, #ffffff 0%, #ff8fa8 3%, #ff2a1a 8%, #ff9a1a 14%, #f5ee28 21%, #2ee65a 29%, #12d4e8 37%, #1e6bff 47%, #0a1a8c 58%, transparent 72%)',
        }}
      />

      {/* Subtle dark vignette overlay specifically on the left side to guarantee crisp text legibility */}
      <div className="absolute inset-y-0 left-0 w-full lg:w-[58%] bg-gradient-to-r from-[#050a2e]/90 via-[#050a2e]/65 to-transparent pointer-events-none z-[1]" />

      {/* Interactive Thermal Mouse Heat Layer (Screen blend, over background, under cards/text) */}
      <ThermalMouseCanvas />

      {/* Main container */}
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center relative z-10 my-auto">
        
        {/* Left Column - Branding & Info */}
        <div className="lg:col-span-7 flex flex-col justify-center max-w-xl mx-auto lg:mx-0">
          
          {/* Logo + Brand name */}
          <div className="flex items-center gap-3.5 mb-10 sm:mb-12">
            <div className="w-11 h-11 rounded-2xl bg-[#0a1a8c]/35 border border-white/[0.14] flex items-center justify-center shadow-inner">
              <Eye className="w-5 h-5 text-[#12d4e8]" />
            </div>
            <div className="flex flex-col">
              <span className="text-white font-bold text-base tracking-tight leading-snug">Fire Watcher</span>
              <span className="text-slate-300 text-xs font-normal">Monitoramento de focos de incêndio</span>
            </div>
          </div>

          {/* Heading with the Thermal Rainbow Palette */}
          <h1 className="text-4xl sm:text-5xl lg:text-[3.25rem] font-bold tracking-tight leading-[1.15] mb-5">
            <span className="text-white block">Proteção ambiental,</span>
            <span 
              className="block text-transparent bg-clip-text font-bold"
              style={{
                backgroundImage: 'linear-gradient(90deg, #1e6bff 0%, #12d4e8 25%, #2ee65a 50%, #f5ee28 75%, #ff9a1a 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              com visão computacional.
            </span>
          </h1>

          {/* Description */}
          <p className="text-slate-300/85 text-sm sm:text-base leading-relaxed mb-10 max-w-lg font-normal">
            Fire Watcher tem como objetivo monitorar em tempo real áreas de preservação, identificando focos e emitindo alertas.
          </p>

          {/* Status / Feature Cards */}
          <div className="space-y-3.5 w-full max-w-md">
            
            {/* Feature 1 - Cold Zone (Cyan Indicator) */}
            <div className="rounded-2xl bg-[#070d2b]/70 border border-white/[0.12] px-5 py-4 backdrop-blur-xl shadow-sm transition-all hover:border-white/[0.22]">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#12d4e8] shadow-[0_0_10px_#12d4e8]" />
                <span className="text-white text-sm font-semibold tracking-tight">Modelo de Machine Learning</span>
              </div>
              <p className="text-slate-300/80 text-xs mt-1 pl-[20px]">
                2 modelos treinados pro foco
              </p>
            </div>

            {/* Feature 2 - Warm Zone (Green Indicator) */}
            <div className="rounded-2xl bg-[#070d2b]/70 border border-white/[0.12] px-5 py-4 backdrop-blur-xl shadow-sm transition-all hover:border-white/[0.22]">
              <div className="flex items-center gap-2.5">
                <span className="w-2.5 h-2.5 rounded-full bg-[#2ee65a] shadow-[0_0_10px_#2ee65a]" />
                <span className="text-white text-sm font-semibold tracking-tight">Alertas em Tempo Real</span>
              </div>
              <p className="text-slate-300/80 text-xs mt-1 pl-[20px]">
                com métricas especializadas
              </p>
            </div>

          </div>
        </div>

        {/* Right Column - Login Card */}
        <div className="lg:col-span-5 w-full flex justify-center lg:justify-end">
          <div 
            className="w-full max-w-[460px] rounded-[28px] p-7 sm:p-9 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.7)] relative overflow-hidden"
            style={{
              backgroundColor: 'rgba(5, 8, 20, 0.45)',
              backdropFilter: 'blur(22px) saturate(130%) brightness(0.8)',
              WebkitBackdropFilter: 'blur(22px) saturate(130%) brightness(0.8)',
              border: '1px solid rgba(255, 255, 255, 0.14)',
              boxShadow: '0 32px 64px -16px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.18)',
            }}
          >
            
            {/* Card Header */}
            <div className="mb-6">
              <h2 className="text-2xl sm:text-[1.65rem] font-bold text-white tracking-tight mb-1">
                Bem-vindo de volta
              </h2>
              <p className="text-slate-400 text-sm">
                Acesse seu painel
              </p>
            </div>

            {/* Social Logins */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              
              {/* Google Button */}
              <button
                type="button"
                className="h-11 rounded-xl bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.12] text-slate-200 text-sm font-medium flex items-center justify-center gap-2.5 transition-all shadow-sm active:scale-[0.98]"
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
                className="h-11 rounded-xl bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.12] text-slate-200 text-sm font-medium flex items-center justify-center gap-2.5 transition-all shadow-sm active:scale-[0.98]"
              >
                <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                <span>GitHub</span>
              </button>

            </div>

            {/* Divider */}
            <div className="relative my-6 flex items-center justify-center">
              <div className="border-t border-white/[0.12] w-full" />
              <span className="absolute bg-[#050814]/90 px-3 text-[10px] sm:text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
                OU COM E-MAIL
              </span>
            </div>

            {/* Form */}
            <form onSubmit={handleLogin} noValidate className="space-y-4">
              
              {/* E-mail / Usuário */}
              <div>
                <label className="text-xs font-medium text-slate-300 mb-1.5 block">
                  E-mail
                </label>
                <input
                  type="text"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    if (errorMessage) setErrorMessage('');
                  }}
                  placeholder="seu@email.com"
                  className="w-full h-11 px-4 bg-white/[0.04] border border-white/[0.12] rounded-xl text-white text-sm placeholder-white/30 focus:outline-none focus:border-[#12d4e8] focus:ring-1 focus:ring-[#12d4e8]/50 transition-all"
                />
              </div>

              {/* Password */}
              <div>
                <label className="text-xs font-medium text-slate-300 mb-1.5 block">
                  Senha
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    if (errorMessage) setErrorMessage('');
                  }}
                  placeholder="••••••••"
                  className="w-full h-11 px-4 bg-white/[0.04] border border-white/[0.12] rounded-xl text-white text-sm placeholder-white/30 focus:outline-none focus:border-[#12d4e8] focus:ring-1 focus:ring-[#12d4e8]/50 transition-all tracking-widest"
                />
              </div>

              {/* Keep connected & Forgot password */}
              <div className="flex items-center justify-between pt-1 pb-2 text-xs sm:text-sm">
                <label className="flex items-center cursor-pointer select-none group">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-white/20 bg-white/5 text-[#12d4e8] focus:ring-0 focus:ring-offset-0 cursor-pointer accent-[#12d4e8]"
                  />
                  <span className="text-slate-300 group-hover:text-white ml-2 transition-colors">
                    Manter conectado
                  </span>
                </label>
                <a
                  href="#"
                  className="text-[#12d4e8] hover:text-[#55e0f0] transition-colors"
                >
                  Esqueci a senha
                </a>
              </div>

              {/* Error feedback if needed */}
              {errorMessage && (
                <div className="px-3.5 py-2 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {/* Submit Button (Warm orange to red gradient) */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 rounded-xl font-bold text-sm sm:text-base text-white transition-all duration-200 flex items-center justify-center cursor-pointer shadow-md hover:shadow-[0_0_24px_rgba(255,42,26,0.45)] hover:opacity-95 active:scale-[0.99] disabled:opacity-85"
                style={{
                  background: 'linear-gradient(90deg, #ff9a1a 0%, #ff2a1a 100%)',
                }}
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                    </svg>
                    <span>Entrando no painel...</span>
                  </div>
                ) : (
                  'Entrar no painel'
                )}
              </button>

            </form>

            {/* Card Footer */}
            <div className="mt-6 text-center text-xs sm:text-sm text-slate-400">
              <span>Novo por aqui? </span>
              <a href="#" className="text-[#12d4e8] hover:text-[#55e0f0] font-medium hover:underline ml-0.5">
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
