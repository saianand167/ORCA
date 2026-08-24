import React from 'react';
import { 
  LayoutDashboard, 
  MessageSquareText, 
  Waves, 
  Fish, 
  Map, 
  AlertTriangle 
} from 'lucide-react';
import { TabType } from './Sidebar';

interface BottomNavProps {
  activeTab: TabType;
  onChangeTab: (tab: TabType) => void;
  warningCount?: number;
}

export const BottomNav: React.FC<BottomNavProps> = ({ activeTab, onChangeTab, warningCount = 0 }) => {
  const items = [
    { id: 'home' as TabType, label: 'Home', icon: LayoutDashboard },
    { id: 'assistant' as TabType, label: 'Assistant', icon: MessageSquareText },
    { id: 'ocean' as TabType, label: 'Ocean', icon: Waves },
    { id: 'pfz' as TabType, label: 'PFZ', icon: Fish },
    { id: 'map' as TabType, label: 'Map', icon: Map },
    { id: 'alerts' as TabType, label: 'Alerts', icon: AlertTriangle, count: warningCount },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-navy-900/95 backdrop-blur-lg border-t border-slate-800 px-2 py-1.5 flex items-center justify-around">
      {items.map((item) => {
        const Icon = item.icon;
        const active = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onChangeTab(item.id)}
            className={`flex flex-col items-center justify-center p-1.5 rounded-lg transition relative ${
              active ? 'text-cyan-400 font-semibold' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Icon className="w-5 h-5" />
            <span className="text-[10px] mt-0.5">{item.label}</span>
            {item.count !== undefined && item.count > 0 && (
              <span className="absolute top-1 right-2 w-2 h-2 rounded-full bg-amber-400"></span>
            )}
          </button>
        );
      })}
    </nav>
  );
};
