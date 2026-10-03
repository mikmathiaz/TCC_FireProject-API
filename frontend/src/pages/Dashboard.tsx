import { useState, useTransition } from 'react';
import { 
  Eye, 
  Flame, 
  Satellite, 
  ShieldAlert, 
  Wind, 
  Droplets, 
  Thermometer, 
  Layers, 
  RefreshCw, 
  LogOut, 
  CheckCircle2, 
  AlertTriangle, 
  ChevronRight, 
  MapPin, 
  Search,
  ExternalLink,
  Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

interface Hotspot {
  id: string;
  aoi: string;
  lat: number;
  lng: number;
  tempCelsius: number;
  confidence: number;
  nbrIndex: number;
  ndviIndex: number;
  severity: 'CRÍTICO' | 'ALTO' | 'MODERADO';
  timestamp: string;
  status: 'Detectado' | 'Notificado' | 'Em Análise';
  satellite: string;
}

const INITIAL_HOTSPOTS: Hotspot[] = [
  {
    id: 'FW-2026-0841',
    aoi: 'Parque Nacional da Chapada dos Veadeiros (GO)',
    lat: -14.1382,
    lng: -47.5140,
    tempCelsius: 428,
    confidence: 99.4,
    nbrIndex: -0.48,
    ndviIndex: 0.12,
    severity: 'CRÍTICO',
    timestamp: 'Há 12 min',
    status: 'Detectado',
    satellite: 'Sentinel-2 MSI (B12/B8A)',
  },
  {
    id: 'FW-2026-0842',
    aoi: 'Parque Nacional da Chapada dos Veadeiros (GO)',
    lat: -14.1495,
    lng: -47.4988,
    tempCelsius: 385,
    confidence: 97.8,
    nbrIndex: -0.36,
    ndviIndex: 0.18,
    severity: 'ALTO',
    timestamp: 'Há 28 min',
    status: 'Notificado',
    satellite: 'Sentinel-2 MSI (B12/B8A)',
  },
  {
    id: 'FW-2026-0839',
    aoi: 'Serra da Canastra - Setor Oeste (MG)',
    lat: -20.2114,
    lng: -46.6542,
    tempCelsius: 340,
    confidence: 94.2,
    nbrIndex: -0.22,
    ndviIndex: 0.25,
    severity: 'MODERADO',
    timestamp: 'Há 1h 14m',
    status: 'Em Análise',
    satellite: 'Sentinel-2 MSI (B12/B8A)',
  },
  {
    id: 'FW-2026-0835',
    aoi: 'Pantanal Matogrossense - Poconé (MT)',
    lat: -16.3218,
    lng: -56.7821,
    tempCelsius: 462,
    confidence: 99.7,
    nbrIndex: -0.55,
    ndviIndex: 0.08,
    severity: 'CRÍTICO',
    timestamp: 'Há 2h 05m',
    status: 'Notificado',
    satellite: 'Sentinel-2 MSI (B12/B8A)',
  },
];

const SPECTRAL_INDICES = [
  {
    id: 'NDVI',
    name: 'NDVI (Vegetação)',
    formula: '(B8 - B4) / (B8 + B4)',
    desc: 'Mede vigor e densidade fotossintética da copa.',
    color: '#2ee65a',
    gradient: 'from-[#12d4e8] via-[#2ee65a] to-[#f5ee28]',
  },
  {
    id: 'NBR',
    name: 'NBR (Severidade)',
    formula: '(B8 - B12) / (B8 + B12)',
    desc: 'Altamente sensível a queimadas e perda de biomassa.',
    color: '#ff2a1a',
    gradient: 'from-[#ff9a1a] via-[#ff2a1a] to-[#731a1a]',
  },
  {
    id: 'NDII',
    name: 'NDII (Umidade)',
    formula: '(B8 - B11) / (B8 + B11)',
    desc: 'Estresse hídrico e teor de umidade foliar.',
    color: '#12d4e8',
    gradient: 'from-[#1e6bff] via-[#12d4e8] to-[#2ee65a]',
  },
  {
    id: 'PSRI',
    name: 'PSRI (Senescência)',
    formula: '(B4 - B2) / B8',
    desc: 'Identifica vegetação ressecada propensa a ignição.',
    color: '#ff9a1a',
    gradient: 'from-[#f5ee28] via-[#ff9a1a] to-[#ff2a1a]',
  },
];

export const Dashboard = () => {
  const { user, logout } = useAuth();
  const [, startTransition] = useTransition();

  const [selectedAOI, setSelectedAOI] = useState('Parque Nacional da Chapada dos Veadeiros (GO)');
  const [selectedHotspot, setSelectedHotspot] = useState<Hotspot | null>(INITIAL_HOTSPOTS[0]);
  const [activeSpectral, setActiveSpectral] = useState('NBR');
  const [isScanning, setIsScanning] = useState(false);
  const [scanSuccess, setScanSuccess] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');

  const handleTriggerScan = () => {
    setIsScanning(true);
    setScanSuccess(false);

    setTimeout(() => {
      startTransition(() => {
        setIsScanning(false);
        setScanSuccess(true);
      });
      setTimeout(() => setScanSuccess(false), 4000);
    }, 2200);
  };

  const filteredHotspots = INITIAL_HOTSPOTS.filter(
    (h) =>
      h.aoi.toLowerCase().includes(searchFilter.toLowerCase()) ||
      h.id.toLowerCase().includes(searchFilter.toLowerCase()) ||
      h.severity.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="min-h-screen w-full bg-[#050a2e] text-white flex flex-col font-sans select-none antialiased relative overflow-x-hidden">
      {/* Background Ambience: Deep Thermal Halos */}
      <div 
        className="fixed top-0 right-1/4 w-[600px] h-[600px] rounded-full pointer-events-none opacity-40 blur-[90px] -z-10"
        style={{
          background: 'radial-gradient(circle, #ff2a1a 0%, #ff9a1a 20%, #1e6bff 50%, transparent 75%)',
        }}
      />
      <div 
        className="fixed bottom-0 left-10 w-[500px] h-[500px] rounded-full pointer-events-none opacity-30 blur-[80px] -z-10"
        style={{
          background: 'radial-gradient(circle, #12d4e8 0%, #0a1a8c 45%, transparent 70%)',
        }}
      />

      {/* Top Navbar */}
      <header className="w-full border-b border-white/[0.10] bg-[#05081e]/80 backdrop-blur-2xl sticky top-0 z-50 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0a1a8c]/40 border border-white/[0.16] flex items-center justify-center shadow-inner">
            <Eye className="w-5 h-5 text-[#12d4e8] animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-white font-bold text-base tracking-tight leading-tight">Fire Watcher</span>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold tracking-wider bg-red-500/20 text-red-400 border border-red-500/30 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping" />
                AOI ATIVA
              </span>
            </div>
            <p className="text-slate-400 text-xs font-normal">
              Sistema de Monitoramento Orbital Sentinel-2 • TCC II
            </p>
          </div>
        </div>

        {/* Telemetry Status Pills (Desktop) */}
        <div className="hidden lg:flex items-center gap-3 text-xs">
          <div className="px-3.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.10] flex items-center gap-2">
            <Satellite className="w-3.5 h-3.5 text-[#12d4e8]" />
            <span className="text-slate-300 font-medium">Satélite Sentinel-2:</span>
            <span className="text-emerald-400 font-semibold">Online (10m)</span>
          </div>

          <div className="px-3.5 py-1.5 rounded-xl bg-white/[0.04] border border-white/[0.10] flex items-center gap-2">
            <Layers className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-300 font-medium">Modelos IA:</span>
            <span className="text-amber-300 font-semibold">2 Ativos</span>
          </div>
        </div>

        {/* User Profile & Logout */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex flex-col text-right">
            <span className="text-white text-xs font-semibold">{user?.name || 'Operador Teste'}</span>
            <span className="text-slate-400 text-[10px]">{user?.role || 'Acesso Painel'}</span>
          </div>

          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#1e6bff] to-[#12d4e8] p-[1px] shadow-sm">
            <div className="w-full h-full rounded-[11px] bg-[#070d2b] flex items-center justify-center font-bold text-xs text-white uppercase">
              {user?.username?.[0] || 'T'}
            </div>
          </div>

          {/* Sair / Logout */}
          <button
            onClick={logout}
            title="Encerrar sessão e voltar ao login"
            className="h-9 px-3 rounded-xl bg-white/[0.06] hover:bg-red-500/20 border border-white/[0.12] hover:border-red-500/30 text-slate-300 hover:text-red-300 text-xs font-medium flex items-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Sair</span>
          </button>
        </div>

      </header>

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

        {/* Section: AOI Control Bar & Scanner */}
        <div className="rounded-2xl bg-[#070d2b]/80 border border-white/[0.12] p-4 sm:p-5 backdrop-blur-xl flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 shadow-lg">
          
          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-[#ff9a1a]" />
              <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Área de Interesse (AOI):
              </label>
            </div>
            <select
              value={selectedAOI}
              onChange={(e) => setSelectedAOI(e.target.value)}
              className="bg-[#050a2e] border border-white/[0.16] rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-[#12d4e8] transition-all cursor-pointer"
            >
              <option value="Parque Nacional da Chapada dos Veadeiros (GO)">Chapada dos Veadeiros (GO)</option>
              <option value="Parque Nacional das Emas (GO)">Parque Nacional das Emas (GO)</option>
              <option value="Serra da Canastra - Setor Oeste (MG)">Serra da Canastra (MG)</option>
              <option value="Pantanal Matogrossense - Poconé (MT)">Pantanal Matogrossense (MT)</option>
              <option value="Floresta Nacional do Jamari (RO)">Floresta Nacional do Jamari (RO)</option>
            </select>
          </div>

          <div className="flex items-center gap-3 self-end md:self-auto">
            {scanSuccess && (
              <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1 animate-fade-in">
                <CheckCircle2 className="w-4 h-4" />
                Varredura Concluída
              </span>
            )}

            <button
              onClick={handleTriggerScan}
              disabled={isScanning}
              className="h-10 px-4 rounded-xl font-semibold text-xs sm:text-sm text-white flex items-center gap-2 transition-all cursor-pointer shadow-md disabled:opacity-60"
              style={{
                background: 'linear-gradient(90deg, #ff9a1a 0%, #ff2a1a 100%)',
              }}
            >
              <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
              <span>{isScanning ? 'Processando Bandas Sentinel-2...' : 'Executar Nova Varredura'}</span>
            </button>
          </div>

        </div>

        {/* Section: KPI Stats (Cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          {/* KPI 1: Focos Ativos */}
          <div className="rounded-2xl bg-[#070d2b]/70 border border-white/[0.12] p-5 backdrop-blur-xl relative overflow-hidden group hover:border-red-500/40 transition-all">
            <div className="absolute top-0 right-0 w-24 h-24 bg-red-600/10 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Focos Ativos</span>
              <div className="w-8 h-8 rounded-lg bg-red-500/20 text-red-400 flex items-center justify-center">
                <Flame className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white tracking-tight">4</span>
              <span className="text-xs font-semibold text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full border border-red-500/20">
                +1 sob suspeita
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-2">
              Validados via sensor MSI Sentinel-2
            </p>
          </div>

          {/* KPI 2: Nível de Risco Médio */}
          <div className="rounded-2xl bg-[#070d2b]/70 border border-white/[0.12] p-5 backdrop-blur-xl relative overflow-hidden group hover:border-amber-500/40 transition-all">
            <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Risco de Ignição</span>
              <div className="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center">
                <ShieldAlert className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white tracking-tight">82%</span>
              <span className="text-xs font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
                Alto / Crítico
              </span>
            </div>
            {/* Heat Ramp Progress Mini Bar */}
            <div className="w-full h-1.5 rounded-full bg-white/10 mt-3 overflow-hidden">
              <div 
                className="h-full rounded-full" 
                style={{ 
                  width: '82%',
                  background: 'linear-gradient(90deg, #2ee65a 0%, #f5ee28 40%, #ff9a1a 70%, #ff2a1a 100%)' 
                }} 
              />
            </div>
          </div>

          {/* KPI 3: Área Monitorada */}
          <div className="rounded-2xl bg-[#070d2b]/70 border border-white/[0.12] p-5 backdrop-blur-xl relative overflow-hidden group hover:border-[#12d4e8]/40 transition-all">
            <div className="absolute top-0 right-0 w-24 h-24 bg-[#12d4e8]/10 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Área Coberta</span>
              <div className="w-8 h-8 rounded-lg bg-[#12d4e8]/20 text-[#12d4e8] flex items-center justify-center">
                <Layers className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white tracking-tight">236.4k</span>
              <span className="text-xs text-slate-300">hectares</span>
            </div>
            <p className="text-slate-400 text-xs mt-2">
              Resolução refinada de 10m/pixel
            </p>
          </div>

          {/* KPI 4: Acurácia da IA */}
          <div className="rounded-2xl bg-[#070d2b]/70 border border-white/[0.12] p-5 backdrop-blur-xl relative overflow-hidden group hover:border-emerald-500/40 transition-all">
            <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="flex items-center justify-between mb-3">
              <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">Acurácia do Modelo</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <CheckCircle2 className="w-4 h-4" />
              </div>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-white tracking-tight">98.4%</span>
              <span className="text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                BDQueimadas
              </span>
            </div>
            <p className="text-slate-400 text-xs mt-2">
              Convergência com histórico INPE
            </p>
          </div>

        </div>

        {/* Section: Main Interactive Viewer & Weather Sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

          {/* Left Column: Satellite Spectral Viewer (8 cols) */}
          <div className="lg:col-span-8 rounded-3xl bg-[#070d2b]/85 border border-white/[0.14] p-5 sm:p-6 backdrop-blur-2xl flex flex-col shadow-2xl relative overflow-hidden">
            
            {/* Header of Viewer */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
              <div>
                <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                  <Satellite className="w-5 h-5 text-[#12d4e8]" />
                  Visor Espectral Orbital — {selectedAOI.split('(')[0].trim()}
                </h3>
                <p className="text-slate-400 text-xs">
                  Sobreposição de anomalias térmicas e índices Sentinel-2
                </p>
              </div>

              {/* Spectral Index Buttons */}
              <div className="flex items-center gap-1.5 bg-[#050a2e] p-1 rounded-xl border border-white/[0.12] overflow-x-auto">
                {SPECTRAL_INDICES.map((idx) => (
                  <button
                    key={idx.id}
                    onClick={() => setActiveSpectral(idx.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer whitespace-nowrap ${
                      activeSpectral === idx.id
                        ? 'bg-white/15 text-white shadow-sm border border-white/20'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {idx.id}
                  </button>
                ))}
              </div>
            </div>

            {/* Satellite Map Simulated Canvas */}
            <div className="relative w-full h-[360px] sm:h-[420px] rounded-2xl bg-[#030617] border border-white/[0.12] overflow-hidden flex items-center justify-center group">
              
              {/* Topographic Background Pattern & Thermal Gradient */}
              <div 
                className="absolute inset-0 opacity-70 transition-all duration-700"
                style={{
                  backgroundImage: `
                    radial-gradient(circle at 45% 40%, rgba(255, 42, 26, 0.45) 0%, rgba(255, 154, 26, 0.25) 25%, rgba(18, 212, 232, 0.12) 50%, rgba(5, 10, 46, 0.95) 75%),
                    linear-gradient(135deg, rgba(7, 13, 43, 0.9) 0%, rgba(2, 4, 16, 0.98) 100%)
                  `,
                }}
              />

              {/* Cartographic Grid overlay */}
              <div 
                className="absolute inset-0 opacity-15 pointer-events-none"
                style={{
                  backgroundImage: `
                    linear-gradient(to right, #12d4e8 1px, transparent 1px),
                    linear-gradient(to bottom, #12d4e8 1px, transparent 1px)
                  `,
                  backgroundSize: '40px 40px',
                }}
              />

              {/* Scanner Line Effect when scanning */}
              {isScanning && (
                <motion.div
                  initial={{ top: '0%' }}
                  animate={{ top: '100%' }}
                  transition={{ duration: 1.8, repeat: Infinity, ease: 'linear' }}
                  className="absolute left-0 right-0 h-1 bg-[#12d4e8] shadow-[0_0_15px_#12d4e8] z-20"
                />
              )}

              {/* Coordinates HUD */}
              <div className="absolute top-3 left-3 bg-[#05081e]/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/[0.12] text-[11px] text-slate-300 font-mono flex items-center gap-2 z-10">
                <span className="w-2 h-2 rounded-full bg-[#12d4e8] animate-ping" />
                AOI LAT -14.1382° | LNG -47.5140° | ESCALA 1:25.000
              </div>

              {/* Spectral Legend */}
              <div className="absolute top-3 right-3 bg-[#05081e]/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/[0.12] text-[11px] text-slate-200 z-10 flex items-center gap-2">
                <span className="font-bold text-[#ff9a1a]">{activeSpectral}:</span>
                <span className="text-slate-400 font-mono">
                  {SPECTRAL_INDICES.find((i) => i.id === activeSpectral)?.formula}
                </span>
              </div>

              {/* Hotspot Pins in the map */}
              {INITIAL_HOTSPOTS.map((hotspot, idx) => {
                const isSelected = selectedHotspot?.id === hotspot.id;
                // Posicionamento espacial ilustrativo
                const leftPos = 25 + idx * 18;
                const topPos = 30 + (idx % 2) * 25;

                return (
                  <button
                    key={hotspot.id}
                    onClick={() => setSelectedHotspot(hotspot)}
                    className="absolute z-20 cursor-pointer transform -translate-x-1/2 -translate-y-1/2 group/pin focus:outline-none"
                    style={{ left: `${leftPos}%`, top: `${topPos}%` }}
                  >
                    <div className="relative flex items-center justify-center">
                      {/* Pulse Ring */}
                      <span className={`absolute w-8 h-8 rounded-full ${hotspot.severity === 'CRÍTICO' ? 'bg-red-500/40 animate-ping' : 'bg-amber-500/30'}`} />
                      
                      {/* Core Pin */}
                      <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center shadow-lg transition-transform ${
                        isSelected 
                          ? 'scale-125 bg-red-600 border-white shadow-[0_0_20px_#ff2a1a]' 
                          : 'bg-[#ff9a1a] border-white/80 group-hover/pin:scale-110'
                      }`}>
                        <Flame className="w-3.5 h-3.5 text-white" />
                      </div>

                      {/* Floating Tooltip Label */}
                      <div className="absolute -bottom-8 whitespace-nowrap bg-[#05081e]/90 text-white text-[10px] font-bold px-2 py-0.5 rounded border border-white/10 opacity-0 group-hover/pin:opacity-100 transition-opacity pointer-events-none">
                        {hotspot.tempCelsius}°C • {hotspot.severity}
                      </div>
                    </div>
                  </button>
                );
              })}

              {/* Selected Hotspot Bottom Sheet / Quick Inspector inside map */}
              <AnimatePresence>
                {selectedHotspot && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    className="absolute bottom-3 inset-x-3 sm:inset-x-6 bg-[#070d2b]/95 border border-white/[0.18] backdrop-blur-xl rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 z-30 shadow-2xl"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-lg bg-red-500/20 border border-red-500/30 text-red-400 flex items-center justify-center shrink-0">
                        <Flame className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-white font-bold text-xs sm:text-sm">{selectedHotspot.id}</span>
                          <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                            {selectedHotspot.severity}
                          </span>
                        </div>
                        <p className="text-slate-400 text-[11px]">
                          Lat: {selectedHotspot.lat}° | Lng: {selectedHotspot.lng}° • Temp Estimada: <strong className="text-amber-300">{selectedHotspot.tempCelsius}°C</strong>
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="text-right hidden sm:block">
                        <span className="text-[10px] text-slate-400 block">Confiança IA</span>
                        <span className="text-xs font-bold text-emerald-400">{selectedHotspot.confidence}%</span>
                      </div>
                      <button 
                        onClick={() => alert(`Alerta operacional para ${selectedHotspot.id} encaminhado à Defesa Civil e Corpo de Bombeiros.`)}
                        className="px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-300 text-xs font-semibold transition-all cursor-pointer"
                      >
                        Despachar Alerta
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

            </div>

            {/* Spectral explanation card */}
            <div className="mt-4 p-3 rounded-xl bg-white/[0.03] border border-white/[0.08] flex items-center justify-between text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <Info className="w-4 h-4 text-[#12d4e8] shrink-0" />
                <span>
                  <strong>{activeSpectral}:</strong> {SPECTRAL_INDICES.find(i => i.id === activeSpectral)?.desc}
                </span>
              </div>
              <span className="text-slate-400 text-[11px] hidden sm:inline font-mono">
                Sensor MSI • Sentinel-2
              </span>
            </div>

          </div>

          {/* Right Column: Environmental Telemetry & Fire Weather (4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-6">

            {/* Weather & Meteorological Telemetry */}
            <div className="rounded-3xl bg-[#070d2b]/85 border border-white/[0.14] p-5 sm:p-6 backdrop-blur-2xl shadow-2xl">
              <h3 className="text-base font-bold text-white tracking-tight mb-4 flex items-center gap-2">
                <Thermometer className="w-5 h-5 text-[#ff2a1a]" />
                Condições Meteorológicas (FWI)
              </h3>

              <div className="space-y-4">
                {/* Temp */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/[0.08]">
                  <div className="flex items-center gap-2.5">
                    <Thermometer className="w-4 h-4 text-red-400" />
                    <div>
                      <span className="text-xs text-slate-400 block">Temperatura do Ar</span>
                      <span className="text-sm font-bold text-white">34.8 °C</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    Elevada
                  </span>
                </div>

                {/* Humidity */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/[0.08]">
                  <div className="flex items-center gap-2.5">
                    <Droplets className="w-4 h-4 text-[#12d4e8]" />
                    <div>
                      <span className="text-xs text-slate-400 block">Umidade Relativa</span>
                      <span className="text-sm font-bold text-white">18 %</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold text-red-400 bg-red-500/10 px-2 py-0.5 rounded border border-red-500/20">
                    Crítica &lt; 20%
                  </span>
                </div>

                {/* Wind */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.03] border border-white/[0.08]">
                  <div className="flex items-center gap-2.5">
                    <Wind className="w-4 h-4 text-emerald-400" />
                    <div>
                      <span className="text-xs text-slate-400 block">Velocidade do Vento</span>
                      <span className="text-sm font-bold text-white">24 km/h (NO)</span>
                    </div>
                  </div>
                  <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                    Propagação Rápida
                  </span>
                </div>

              </div>

              {/* Fire Weather Danger Badge */}
              <div className="mt-5 p-4 rounded-2xl bg-gradient-to-r from-red-600/20 to-orange-600/20 border border-red-500/30">
                <div className="flex items-center gap-2 text-red-400 font-bold text-xs uppercase tracking-wider mb-1">
                  <AlertTriangle className="w-4 h-4" />
                  Índice de Perigo Meteorológico
                </div>
                <p className="text-slate-300 text-xs leading-relaxed">
                  Baixa umidade conjugada com ventos constantes eleva o risco de combustão espontânea e rápida expansão do perímetro.
                </p>
              </div>

            </div>

            {/* Academic Information Card (TCC Context) */}
            <div className="rounded-3xl bg-[#070d2b]/85 border border-white/[0.14] p-5 backdrop-blur-2xl shadow-2xl flex-1 flex flex-col justify-between">
              <div>
                <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-2 text-slate-300">
                  Validação Cruzada
                </h4>
                <p className="text-slate-400 text-xs leading-relaxed">
                  Os focos detectados no espectro de infravermelho de ondas curtas (SWIR 1 e SWIR 2) do satélite Sentinel-2 são correlacionados com o banco do INPE (BDQueimadas).
                </p>
              </div>

              <div className="pt-4 border-t border-white/[0.08] mt-4 flex items-center justify-between text-xs text-slate-400">
                <span>Versão do Pipeline: <strong>1.0.4-dev</strong></span>
                <span className="text-[#12d4e8] font-medium flex items-center gap-1">
                  Documentação <ChevronRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>

          </div>

        </div>

        {/* Section: Live Hotspots Feed Table */}
        <div className="rounded-3xl bg-[#070d2b]/85 border border-white/[0.14] p-5 sm:p-6 backdrop-blur-2xl shadow-2xl">
          
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                <Flame className="w-5 h-5 text-red-400" />
                Registros de Ocorrências em Tempo Real
              </h3>
              <p className="text-slate-400 text-xs">
                Filtre por código de alerta, severidade ou área de preservação
              </p>
            </div>

            {/* Search Input */}
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="Filtrar ocorrência..."
                className="w-full h-9 pl-9 pr-3 rounded-xl bg-[#050a2e] border border-white/[0.12] text-xs text-white placeholder-slate-400 focus:outline-none focus:border-[#12d4e8]"
              />
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/[0.10] text-slate-400 uppercase tracking-wider font-semibold">
                  <th className="py-3 px-3">Código</th>
                  <th className="py-3 px-3">Área de Preservação</th>
                  <th className="py-3 px-3">Severidade</th>
                  <th className="py-3 px-3">Temperatura</th>
                  <th className="py-3 px-3">NBR / NDVI</th>
                  <th className="py-3 px-3">Confiança</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3 text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.06]">
                {filteredHotspots.map((item) => (
                  <tr 
                    key={item.id}
                    onClick={() => setSelectedHotspot(item)}
                    className="hover:bg-white/[0.03] transition-colors cursor-pointer group"
                  >
                    <td className="py-3 px-3 font-mono font-bold text-white">
                      {item.id}
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {item.aoi}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded font-bold text-[10px] border ${
                        item.severity === 'CRÍTICO'
                          ? 'bg-red-500/20 text-red-400 border-red-500/30'
                          : item.severity === 'ALTO'
                          ? 'bg-orange-500/20 text-orange-400 border-orange-500/30'
                          : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
                      }`}>
                        {item.severity}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-amber-300 font-mono">
                      {item.tempCelsius} °C
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-300">
                      NBR: {item.nbrIndex} • NDVI: {item.ndviIndex}
                    </td>
                    <td className="py-3 px-3 font-semibold text-emerald-400">
                      {item.confidence}%
                    </td>
                    <td className="py-3 px-3 text-slate-400">
                      {item.status} ({item.timestamp})
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedHotspot(item);
                        }}
                        className="p-1.5 rounded-lg bg-white/[0.05] hover:bg-[#12d4e8]/20 text-slate-300 hover:text-[#12d4e8] transition-all cursor-pointer"
                        title="Ver no Visor Orbital"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-white/[0.08] py-4 px-6 text-center text-xs text-slate-400">
        Fire Watcher © 2026 — Trabalho de Conclusão de Curso (TCC II) • Bacharelado em Engenharia da Computação
      </footer>

    </div>
  );
};

export default Dashboard;
