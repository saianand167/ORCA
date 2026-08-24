import React from 'react';
import { 
  LayoutDashboard, 
  MessageSquareText, 
  Waves, 
  Fish, 
  Map, 
  AlertTriangle, 
  Database,
  ShieldCheck
} from 'lucide-react';

export type TabType = 'home' | 'assistant' | 'ocean' | 'pfz' | 'map' | 'alerts' | 'sources';

interface SidebarProps {
  activeTab: TabType;
  onChangeTab: (tab: TabType) => void;
  warningCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onChangeTab, warningCount = 0 }) => {
  const navItems = [
    { id: 'home' as TabType, label: 'Home Dashboard', icon: LayoutDashboard },
    { id: 'assistant' as TabType, label: 'Marine Assistant', icon: MessageSquareText, badge: 'AI' },
    { id: 'ocean' as TabType, label: 'Ocean Conditions', icon: Waves },
    { id: 'pfz' as TabType, label: 'Fishing Zones', icon: Fish },
    { id: 'map' as TabType, label: 'Map Explorer', icon: Map },
    { id: 'alerts' as TabType, label: 'Alerts & Warnings', icon: AlertTriangle, count: warningCount },
    { id: 'sources' as TabType, label: 'Data Sources', icon: Database },
  ];

  return (
    <aside className="hidden md:flex flex-col w-64 border-r border-slate-800/80 bg-navy-900/40 p-4 shrink-0 justify-between">
      <div className="space-y-1.5">
        <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChangeTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition ${
                active
                  ? 'bg-gradient-to-r from-cyan-500/15 to-blue-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${active ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                  {item.badge}
                </span>
              )}
              {item.count !== undefined && item.count > 0 && (
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {item.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Safety Notice Footer Card */}
      <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1.5">
        <div className="flex items-center gap-1.5 text-cyan-400 font-semibold">
          <ShieldCheck className="w-4 h-4" />
          <span>Decision Support</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          ORCA correlates satellite and oceanic sensors. Always verify official marine notices before voyage.
        </p>
      </div>
    </aside>
  );
};
