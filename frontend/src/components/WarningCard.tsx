import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, Clock } from 'lucide-react';
import { MarineWarning } from '../types';

interface WarningCardProps {
  warnings: MarineWarning[];
}

export const WarningCard: React.FC<WarningCardProps> = ({ warnings }) => {
  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'VERY HIGH':
        return {
          bg: 'bg-rose-50 border-rose-200 text-rose-800',
          badge: 'bg-rose-100 text-rose-800 border-rose-300',
          icon: ShieldAlert
        };
      case 'HIGH':
        return {
          bg: 'bg-amber-50 border-amber-200 text-amber-800',
          badge: 'bg-amber-100 text-amber-800 border-amber-300',
          icon: ShieldAlert
        };
      case 'MODERATE':
        return {
          bg: 'bg-yellow-50 border-yellow-200 text-yellow-800',
          badge: 'bg-yellow-100 text-yellow-800 border-yellow-300',
          icon: AlertTriangle
        };
      default:
        return {
          bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
          badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
          icon: CheckCircle2
        };
    }
  };

  return (
    <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-2xl bg-amber-50 text-amber-600">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">Marine Warnings & Advisories</h3>
            <p className="text-xs text-slate-400">IMD & INCOIS Coastal Bulletin</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full font-bold bg-slate-100 text-slate-600">
          {warnings.length} {warnings.length === 1 ? 'ALERT' : 'ALERTS'}
        </span>
      </div>

      <div className="space-y-3">
        {warnings.map((w, idx) => {
          const style = getSeverityStyle(w.severity);
          const Icon = style.icon;
          return (
            <div key={idx} className={`p-4 rounded-2xl border ${style.bg} space-y-2`}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span className="text-xs font-bold">{w.headline}</span>
                </div>
                <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-full border uppercase shrink-0 ${style.badge}`}>
                  {w.severity}
                </span>
              </div>
              <p className="text-xs leading-relaxed opacity-90">
                {w.description}
              </p>
              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/60 text-[11px] opacity-75">
                <span>Affected: {w.affected_areas.join(', ')}</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Valid: {w.valid_until}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
