import React, { useState } from 'react';
import { 
  Waves, 
  Wind, 
  Fish, 
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  MapPin, 
  ArrowRight,
  Send,
  Compass,
  ThermometerSun,
  Navigation,
  Sparkles,
  Calendar,
  X,
  Bot
} from 'lucide-react';
import { 
  LocationInfo, 
  UserRole, 
  WeatherData, 
  OceanData, 
  PFZData, 
  MarineWarning, 
  RiskAssessment,
  PFZLocation
} from '../types';
import { MarineMap } from '../components/MarineMap';
import { QuickQuestions } from '../components/QuickQuestions';
import { TabType } from '../components/Sidebar';

interface HomeProps {
  location: LocationInfo;
  userRole: UserRole;
  weather: WeatherData | null;
  ocean: OceanData | null;
  pfz: PFZData | null;
  warnings: MarineWarning[];
  risk: RiskAssessment | null;
  onSelectPrompt: (prompt: string) => void;
  onNavigateTab: (tab: TabType) => void;
  onSelectPfzOnMap?: (pfz: PFZLocation) => void;
}

export const Home: React.FC<HomeProps> = ({
  location,
  userRole,
  weather,
  ocean,
  pfz,
  warnings,
  risk,
  onSelectPrompt,
  onNavigateTab,
  onSelectPfzOnMap
}) => {
  const [showAnnouncement, setShowAnnouncement] = useState(true);
  const [quickChatInput, setQuickChatInput] = useState('');

  const nearestPfz = pfz?.nearest_pfz || (pfz?.locations && pfz.locations.length > 0 ? pfz.locations[0] : null);

  const getRiskBadge = () => {
    if (!risk) return { bg: 'bg-emerald-50 text-emerald-800 border-emerald-200', text: 'LOW' };
    if (risk.risk_level === 'LOW') return { bg: 'bg-emerald-50 text-emerald-800 border-emerald-200', text: 'LOW' };
    if (risk.risk_level === 'MODERATE') return { bg: 'bg-teal-50 text-teal-800 border-teal-200', text: 'MODERATE' };
    if (risk.risk_level === 'HIGH') return { bg: 'bg-amber-50 text-amber-800 border-amber-200', text: 'HIGH' };
    return { bg: 'bg-rose-50 text-rose-800 border-rose-200', text: 'VERY HIGH' };
  };

  const handleQuickChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickChatInput.trim()) return;
    onSelectPrompt(quickChatInput.trim());
    setQuickChatInput('');
  };

  const roleTitles: Record<UserRole, string> = {
    fisherman: 'Fisherman Decision Support',
    ocean_researcher: 'Oceanographic Research Suite',
    ship_operator: 'Vessel Route & Maritime Safety'
  };

  return (
    <div className="max-w-[1600px] mx-auto space-y-6 pb-12">
      {/* 1. Top Section: Header & Active Notice */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white/80 backdrop-blur-sm p-6 rounded-3xl border border-slate-200/80 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              {location.name} Marine Intelligence
            </h1>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200">
              {roleTitles[userRole]}
            </span>
          </div>
          <p className="text-xs sm:text-sm text-slate-500 mt-1 flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-teal-600 shrink-0" />
            {location.state} • {location.coastal_body} • Coordinates: {location.coordinates.latitude.toFixed(2)}°N, {location.coordinates.longitude.toFixed(2)}°E
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <div className="text-right hidden sm:block">
            <span className="text-xs font-bold text-slate-700 block">
              {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
            <span className="text-[11px] text-emerald-600 font-semibold flex items-center justify-end gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              INCOIS & IMD Telemetry Active
            </span>
          </div>
          <button
            onClick={() => onNavigateTab('assistant')}
            className="px-4 py-2.5 rounded-2xl bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold shadow-md shadow-teal-600/20 flex items-center gap-2 transition"
          >
            <Bot className="w-4 h-4" />
            <span>Ask AI Assistant</span>
          </button>
        </div>
      </div>

      {/* 2. Announcement Banner */}
      {showAnnouncement && warnings.length > 0 && (
        <div className="p-4 rounded-2xl bg-amber-50/90 border border-amber-200 text-amber-900 shadow-xs flex items-center justify-between gap-4 text-xs sm:text-sm">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-xl bg-amber-100 text-amber-700 shrink-0">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <span className="font-extrabold uppercase tracking-wide text-amber-800 mr-2">
                ACTIVE ADVISORY:
              </span>
              <span className="text-slate-700 font-medium">
                {warnings[0].headline} — <em>{warnings[0].source}</em>
              </span>
            </div>
          </div>
          <button 
            onClick={() => setShowAnnouncement(false)}
            className="p-1 rounded-lg text-amber-600 hover:bg-amber-100 transition shrink-0"
            title="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 3. Top Key Metrics Row (4 Spacious Cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Metric 1: Operational Risk */}
        <div className="p-5 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              OPERATIONAL RISK
            </span>
            <span className={`text-xs font-extrabold px-2.5 py-0.5 rounded-full border ${getRiskBadge().bg}`}>
              {risk?.risk_level || 'MODERATE'} ({risk?.score || 31}/100)
            </span>
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">
              {risk?.safe_for_operations ? 'Operations Feasible' : 'Caution Required'}
            </div>
            <p className="text-xs text-slate-500 mt-1 truncate">
              {risk?.summary || 'Standard coastal conditions.'}
            </p>
          </div>
          {/* Progress bar */}
          <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden">
            <div 
              className="h-full bg-teal-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.max(10, Math.min(100, risk?.score || 31))}%` }}
            />
          </div>
        </div>

        {/* Metric 2: Significant Wave */}
        <div className="p-5 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              SIG WAVE HEIGHT
            </span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              Period {ocean?.wave_period_s || 8.2}s
            </span>
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">
              {ocean?.significant_wave_height_m || 1.4} <span className="text-sm font-normal text-slate-400">m</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Swell: {ocean?.swell_height_m || 1.1}m @ {ocean?.swell_period_s || 11.5}s ({ocean?.wave_direction_deg || 140}°)
            </p>
          </div>
          <div className="text-[11px] text-teal-700 font-semibold flex items-center gap-1">
            <Waves className="w-3.5 h-3.5" /> INCOIS Ocean State Forecast
          </div>
        </div>

        {/* Metric 3: Wind & Weather */}
        <div className="p-5 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              SURFACE WIND
            </span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200">
              {weather?.wind_direction_cardinal || 'SE'} ({weather?.wind_direction_deg || 135}°)
            </span>
          </div>
          <div>
            <div className="text-2xl font-black text-slate-900">
              {weather?.wind_speed_ms || 5.1} <span className="text-sm font-normal text-slate-400">m/s</span>
              <span className="text-sm font-semibold text-purple-700 ml-2">({weather?.wind_speed_knots || 10.0} kts)</span>
            </div>
            <p className="text-xs text-slate-500 mt-1 truncate">
              {weather?.condition || 'Partly Cloudy'} • Temp: {weather?.temperature_c || 31.2}°C
            </p>
          </div>
          <div className="text-[11px] text-purple-700 font-semibold flex items-center gap-1">
            <Wind className="w-3.5 h-3.5" /> IMD Coastal Weather Station
          </div>
        </div>

        {/* Metric 4: Nearest PFZ */}
        <div className="p-5 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
              NEAREST PFZ
            </span>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              {nearestPfz ? nearestPfz.sector : 'Active'}
            </span>
          </div>
          <div>
            <div className="text-2xl font-black text-emerald-700">
              {nearestPfz ? `${nearestPfz.distance_km} km` : '28.4 km'}
              <span className="text-xs font-normal text-slate-400 ml-1.5">
                ({nearestPfz ? `${nearestPfz.distance_nm} nm` : '15.3 nm'})
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1 truncate">
              Depth: {nearestPfz?.depth_m || '45-65'}m • Species: {nearestPfz?.fish_species_likely.slice(0, 2).join(', ') || 'Tuna, Mackerel'}
            </p>
          </div>
          <div className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
            <Fish className="w-3.5 h-3.5" /> INCOIS Satellite Advisory
          </div>
        </div>
      </div>

      {/* 4. Main Two-Column Layout (7 Columns Left, 5 Columns Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Interactive Map & Quick Questions (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Situation Map Card */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-teal-600" />
                  Live Marine Situation Map — {location.name}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Interactive GIS layer with Potential Fishing Zones (PFZ), Coastal Corridors & Marine Protected Areas
                </p>
              </div>
              <button
                onClick={() => onNavigateTab('map')}
                className="text-xs font-bold text-teal-600 hover:text-teal-800 flex items-center gap-1 shrink-0"
              >
                <span>Full Map</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>

            <MarineMap
              location={location}
              pfzLocations={pfz?.locations || []}
              selectedPfz={nearestPfz}
              height="380px"
              onAskAboutPfz={(p) => {
                onSelectPrompt(`Provide navigation route, wave conditions, and catch advice for ${p.id} (${p.distance_km}km, bearing ${p.sector}).`);
              }}
            />
          </div>

          {/* Quick Inquiry Prompts */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-3">
            <QuickQuestions
              userRole={userRole}
              locationName={location.name}
              onSelectPrompt={onSelectPrompt}
            />
          </div>
        </div>

        {/* Right Column: Telemetry Breakdown & Quick AI Chat (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Ocean Parameters Breakdown */}
          <div className="p-6 rounded-3xl bg-white border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Compass className="w-4 h-4 text-teal-600" />
                Detailed Oceanographic Telemetry
              </h3>
              <button
                onClick={() => onNavigateTab('ocean')}
                className="text-xs font-bold text-teal-600 hover:text-teal-800"
              >
                View Charts
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-slate-400 font-medium flex items-center gap-1">
                  <ThermometerSun className="w-3.5 h-3.5 text-amber-500" /> Sea Surface Temp
                </span>
                <p className="text-lg font-black text-slate-800">
                  {ocean?.sea_surface_temperature_c || 29.4}°C
                </p>
                <span className="text-[10px] text-emerald-600 font-semibold">Thermal Front Normal</span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-slate-400 font-medium flex items-center gap-1">
                  <Navigation className="w-3.5 h-3.5 text-blue-500" /> Surface Current
                </span>
                <p className="text-lg font-black text-slate-800">
                  {ocean?.surface_current_speed_ms || 0.42} m/s
                </p>
                <span className="text-[10px] text-slate-500 font-medium">Dir: {ocean?.surface_current_direction_deg || 45}° NE</span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-slate-400 font-medium flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-500" /> Chlorophyll-a
                </span>
                <p className="text-lg font-black text-slate-800">
                  {ocean?.chlorophyll_mg_m3 || 0.85} mg/m³
                </p>
                <span className="text-[10px] text-emerald-600 font-semibold">OCM Satellite Feed</span>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
                <span className="text-slate-400 font-medium flex items-center gap-1">
                  <Waves className="w-3.5 h-3.5 text-purple-500" /> Mixed Layer Depth
                </span>
                <p className="text-lg font-black text-slate-800">
                  {ocean?.mixed_layer_depth_m || 24.5} m
                </p>
                <span className="text-[10px] text-slate-500 font-medium">Thermocline boundary</span>
              </div>
            </div>
          </div>

          {/* Quick Interactive Assistant Box */}
          <div className="p-6 rounded-3xl bg-gradient-to-br from-teal-500/10 via-emerald-500/5 to-white border border-teal-200/80 shadow-xs space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-2xl bg-teal-600 text-white flex items-center justify-center shadow-md shadow-teal-600/20 shrink-0">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Ask ORCA Intelligence</h3>
                <p className="text-xs text-slate-500">Autonomous reasoning with multi-agent coordination</p>
              </div>
            </div>

            <form onSubmit={handleQuickChatSubmit} className="flex items-center gap-2">
              <input
                type="text"
                value={quickChatInput}
                onChange={(e) => setQuickChatInput(e.target.value)}
                placeholder={`Is it safe to venture tomorrow near ${location.name}?`}
                className="flex-1 bg-white text-xs sm:text-sm text-slate-800 placeholder-slate-400 px-4 py-2.5 rounded-2xl border border-slate-200 focus:outline-none focus:border-teal-500 shadow-xs"
              />
              <button
                type="submit"
                disabled={!quickChatInput.trim()}
                className="p-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-2xl font-medium disabled:opacity-40 shadow-sm transition shrink-0"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>

            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
              <span>Supports English, Telugu, Hindi, Tamil</span>
              <button 
                onClick={() => onNavigateTab('assistant')} 
                className="font-bold text-teal-700 hover:underline"
              >
                Open Full Chat →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
