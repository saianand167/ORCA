import React from 'react';
import { 
  Compass, 
  MapPin, 
  ChevronDown,
  LayoutDashboard,
  MessageSquareText,
  Waves,
  Fish,
  Map as MapIcon,
  AlertTriangle,
  Database,
  Radio
} from 'lucide-react';
import { LocationInfo, UserRole, DataQuality } from '../types';
import { TabType } from './Sidebar';

interface HeaderProps {
  locations: LocationInfo[];
  selectedLocation: LocationInfo;
  onSelectLocation: (loc: LocationInfo) => void;
  userRole: UserRole;
  onChangeUserRole: (role: UserRole) => void;
  dataQuality?: DataQuality;
  activeTab: TabType;
  onChangeTab: (tab: TabType) => void;
  isDemoMode?: boolean;
  onToggleDemoMode?: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  locations,
  selectedLocation,
  onSelectLocation,
  userRole,
  onChangeUserRole,
  dataQuality = 'LIVE',
  activeTab,
  onChangeTab,
  isDemoMode = false,
  onToggleDemoMode
}) => {
  const tabs = [
    { id: 'home' as TabType, label: 'Overview', icon: LayoutDashboard },
    { id: 'assistant' as TabType, label: 'AI Assistant', icon: MessageSquareText, badge: 'AI' },
    { id: 'ocean' as TabType, label: 'Ocean State', icon: Waves },
    { id: 'pfz' as TabType, label: 'Fishing Zones', icon: Fish },
    { id: 'map' as TabType, label: 'Map Explorer', icon: MapIcon },
    { id: 'alerts' as TabType, label: 'Alerts', icon: AlertTriangle },
    { id: 'sources' as TabType, label: 'Data Sources', icon: Database },
  ];

  const roleLabels: Record<UserRole, { label: string; icon: string }> = {
    fisherman: { label: 'Fisherman', icon: '🎣' },
    ocean_researcher: { label: 'Researcher', icon: '🔬' },
    ship_operator: { label: 'Operator', icon: '🚢' }
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-slate-200/80 shadow-xs">
      <div className="max-w-[1600px] mx-auto px-4 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand Emblem & Location Dropdown */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-teal-600 via-teal-500 to-emerald-400 text-white flex items-center justify-center shadow-md shadow-teal-500/20">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 leading-none">
                <span className="text-base font-extrabold tracking-tight text-slate-900">
                  ORCA
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-teal-50 text-teal-700 border border-teal-200/80">
                  ISRO SIH
                </span>
              </div>
              <span className="text-[11px] text-slate-400 font-medium hidden sm:inline">
                Marine Intelligence
              </span>
            </div>
          </div>

          <div className="h-6 w-px bg-slate-200 mx-1 hidden sm:block" />

          {/* Location Selector Dropdown */}
          <div className="relative flex items-center">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200/80 text-xs font-semibold text-slate-700 transition cursor-pointer">
              <MapPin className="w-3.5 h-3.5 text-teal-600 shrink-0" />
              <select
                value={selectedLocation.id}
                onChange={(e) => {
                  const loc = locations.find((l) => l.id === e.target.value);
                  if (loc) onSelectLocation(loc);
                }}
                className="bg-transparent text-slate-800 font-bold focus:outline-none cursor-pointer pr-4 appearance-none text-xs"
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id} className="bg-white text-slate-800">
                    {loc.name}, {loc.state}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3 h-3 text-slate-400 absolute right-2.5 pointer-events-none" />
            </div>
          </div>
        </div>

        {/* Center: Clean Segmented Navigation (No wrapping, properly spaced) */}
        <nav className="hidden xl:flex items-center p-1 bg-slate-100/90 rounded-2xl border border-slate-200/80 shadow-xs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onChangeTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  active
                    ? 'bg-white text-teal-800 font-bold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? 'text-teal-600' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className="text-[9px] font-extrabold px-1 rounded bg-teal-100 text-teal-700">
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right: User Role & Live Telemetry Badge */}
        <div className="flex items-center gap-2.5 shrink-0">
          {/* User Role Switcher */}
          <div className="flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200/80 text-xs">
            {(['fisherman', 'ocean_researcher', 'ship_operator'] as UserRole[]).map((role) => {
              const active = userRole === role;
              return (
                <button
                  key={role}
                  onClick={() => onChangeUserRole(role)}
                  className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition ${
                    active
                      ? 'bg-white text-slate-900 font-bold shadow-xs'
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <span className="text-xs">{roleLabels[role].icon}</span>
                  <span className="hidden md:inline">{roleLabels[role].label}</span>
                </button>
              );
            })}
          </div>

          {/* Mode Switcher: Live vs Demo Squall Simulation */}
          {onToggleDemoMode ? (
            <button
              onClick={() => onToggleDemoMode(!isDemoMode)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition shadow-xs cursor-pointer ${
                isDemoMode
                  ? 'bg-amber-100 text-amber-900 border border-amber-300 hover:bg-amber-200'
                  : 'bg-emerald-50 text-emerald-800 border border-emerald-200/80 hover:bg-emerald-100'
              }`}
              title={isDemoMode ? 'Click to switch to Live Telemetry' : 'Click to simulate severe cyclonic squall condition'}
            >
              <span className={`w-2 h-2 rounded-full ${isDemoMode ? 'bg-amber-500 animate-ping' : 'bg-emerald-500 animate-pulse'}`} />
              <span className="hidden sm:inline">{isDemoMode ? 'DEMO SIMULATION' : 'LIVE TELEMETRY'}</span>
              <span className="sm:hidden">{isDemoMode ? 'DEMO' : 'LIVE'}</span>
            </button>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200/80 text-xs font-bold shadow-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="hidden sm:inline">{dataQuality}</span>
            </div>
          )}
        </div>
      </div>

      {/* Sub-navigation bar for tablets / medium screens */}
      <div className="xl:hidden flex items-center justify-start gap-1 px-4 py-1.5 border-t border-slate-100 overflow-x-auto bg-slate-50/50">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onChangeTab(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold whitespace-nowrap shrink-0 transition ${
                active
                  ? 'bg-teal-500 text-white font-bold'
                  : 'text-slate-600 hover:bg-slate-200/60'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
