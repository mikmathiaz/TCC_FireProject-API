import { useState } from 'react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Login attempt:', { email, rememberMe });
  };

  return (
    <div className="min-h-screen w-full bg-[#0c0e17] text-white flex items-center justify-center relative overflow-hidden font-sans select-none antialiased px-4 py-8 sm:px-6 lg:px-12">
      {/* Ambient background glows */}
      <div 
        className="absolute -top-[15%] -left-[10%] w-[650px] h-[650px] rounded-full pointer-events-none opacity-40 blur-[130px]"
        style={{
          background: 'radial-gradient(circle, rgba(99, 102, 241, 0.45) 0%, rgba(79, 70, 229, 0.2) 50%, transparent 75%)'
        }}
      />
      <div 
        className="absolute -bottom-[20%] right-[5%] w-[600px] h-[600px] rounded-full pointer-events-none opacity-25 blur-[140px]"
        style={{
          background: 'radial-gradient(circle, rgba(20, 184, 166, 0.4) 0%, rgba(13, 148, 136, 0.15) 50%, transparent 75%)'
        }}
      />
      <div 
        className="absolute top-[40%] right-[35%] w-[450px] h-[450px] rounded-full pointer-events-none opacity-15 blur-[120px]"
        style={{
          background: 'radial-gradient(circle, rgba(168, 85, 247, 0.3) 0%, transparent 70%)'
        }}
      />

      {/* Main container */}
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center relative z-10 my-auto">
        
        {/* Left Column - Branding & Info */}
        <div className="lg:col-span-7 flex flex-col justify-center max-w-xl mx-auto lg:mx-0">
          
          {/* Logo + Brand name */}
          <div className="flex items-center gap-3.5 mb-10 sm:mb-12">
            <div className="w-11 h-11 rounded-2xl bg-[#21243d] border border-white/[0.08] flex items-center justify-center shadow-inner">
              <span className="text-[#a5b4fc] font-bold text-lg leading-none">N</span>
            </div>
            <div className="flex flex-col">
              <span className="text-white font-bold text-base tracking-tight leading-snug">Nexo</span>
              <span className="text-slate-400 text-xs font-normal">Sistema pessoal de IA</span>
            </div>
          </div>

          {/* Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-[3.25rem] font-bold tracking-tight leading-[1.15] mb-5">
            <span className="text-white block">Sua inteligência,</span>
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-[#67e8f9] via-[#c084fc] to-[#f472b6]">
              em um só lugar.
            </span>
          </h1>

          {/* Description */}
          <p className="text-slate-400 text-sm sm:text-base leading-relaxed mb-10 max-w-lg font-normal">
            O Nexo reúne seus projetos, contextos e agentes em um painel único. Faça login para retomar de onde parou.
          </p>

          {/* Status / Feature Cards */}
          <div className="space-y-3.5 w-full max-w-md">
            
            {/* Feature 1 */}
            <div className="rounded-2xl bg-[#141824]/75 border border-slate-700/30 px-5 py-4 backdrop-blur-md shadow-sm transition-all hover:border-slate-600/40">
              <div className="flex items-center gap-2.5">
                <span className="w-2 h-2 rounded-full bg-[#34d399] shadow-[0_0_10px_#34d399]" />
                <span className="text-white text-sm font-semibold tracking-tight">Agentes sincronizados</span>
              </div>
              <p className="text-slate-400 text-xs mt-1 pl-[18px]">
                3 agentes ativos em seus projetos
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-2xl bg-[#141824]/75 border border-slate-700/30 px-5 py-4 backdrop-blur-md shadow-sm transition-all hover:border-slate-600/40">
              <div className="flex items-center gap-2.5">
                <span className="w-2 h-2 rounded-full bg-slate-300 shadow-[0_0_8px_rgba(255,255,255,0.7)]" />
                <span className="text-white text-sm font-semibold tracking-tight">Contexto persistente</span>
              </div>
              <p className="text-slate-400 text-xs mt-1 pl-[18px]">
                Conversas salvas com histórico completo
              </p>
            </div>

          </div>
        </div>

        {/* Right Column - Login Card */}
        <div className="lg:col-span-5 w-full flex justify-center lg:justify-end">
          <div className="w-full max-w-[460px] rounded-[28px] bg-[#151926]/85 backdrop-blur-2xl border border-white/[0.08] p-7 sm:p-9 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.65),inset_0_1px_0_rgba(255,255,255,0.1)]">
            
            {/* Card Header */}
            <div className="mb-6">
              <h2 className="text-2xl sm:text-[1.65rem] font-bold text-white tracking-tight mb-1">
                Bem-vindo de volta
              </h2>
              <p className="text-slate-400 text-sm">
                Acesse seu painel pessoal
              </p>
            </div>

            {/* Social Logins */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              
              {/* Google Button */}
              <button
                type="button"
                className="h-11 rounded-xl bg-[#1e2332]/90 hover:bg-[#262c3f] border border-white/[0.07] text-slate-200 text-sm font-medium flex items-center justify-center gap-2.5 transition-all shadow-sm active:scale-[0.98]"
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
                className="h-11 rounded-xl bg-[#1e2332]/90 hover:bg-[#262c3f] border border-white/[0.07] text-slate-200 text-sm font-medium flex items-center justify-center gap-2.5 transition-all shadow-sm active:scale-[0.98]"
              >
                <svg className="w-4 h-4 fill-white" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
                </svg>
                <span>GitHub</span>
              </button>

            </div>

            {/* Divider */}
            <div className="relative my-6 flex items-center justify-center">
              <div className="border-t border-slate-700/40 w-full" />
              <span className="absolute bg-[#151926] px-3 text-[10px] sm:text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
                OU COM E-MAIL
              </span>
            </div>

            {/* Form */}
            <form onSubmit={handleLogin} className="space-y-4">
              
              {/* E-mail */}
              <div>
                <label className="text-xs font-medium text-slate-300 mb-1.5 block">
                  E-mail
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="voce@nexo.app"
                  className="w-full h-11 px-4 bg-[#1f2434]/80 border border-slate-700/50 rounded-xl text-white text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/50 transition-all"
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
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full h-11 px-4 bg-[#1f2434]/80 border border-slate-700/50 rounded-xl text-white text-sm placeholder-slate-400 focus:outline-none focus:border-indigo-500/80 focus:ring-1 focus:ring-indigo-500/50 transition-all tracking-widest"
                />
              </div>

              {/* Keep connected & Forgot password */}
              <div className="flex items-center justify-between pt-1 pb-2 text-xs sm:text-sm">
                <label className="flex items-center cursor-pointer select-none group">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-600 bg-slate-800/90 text-indigo-500 focus:ring-0 focus:ring-offset-0 cursor-pointer accent-indigo-500"
                  />
                  <span className="text-slate-400 group-hover:text-slate-300 ml-2 transition-colors">
                    Manter conectado
                  </span>
                </label>
                <a
                  href="#"
                  className="text-slate-400 hover:text-slate-200 transition-colors"
                >
                  Esqueci a senha
                </a>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                className="w-full h-12 rounded-xl font-semibold text-sm sm:text-base text-slate-900 bg-gradient-to-r from-[#a5f3fc] via-[#c4b5fd] to-[#f472b6] hover:opacity-95 hover:shadow-[0_0_24px_rgba(244,114,182,0.3)] active:scale-[0.99] transition-all duration-200 flex items-center justify-center cursor-pointer"
              >
                Entrar no painel
              </button>

            </form>

            {/* Card Footer */}
            <div className="mt-6 text-center text-xs sm:text-sm text-slate-400">
              <span>Novo por aqui? </span>
              <a href="#" className="text-white font-medium hover:underline ml-0.5">
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
