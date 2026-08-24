import React from 'react';
import { AlertTriangle, Radio } from 'lucide-react';
import { LocationInfo, MarineWarning } from '../types';
import { WarningCard } from '../components/WarningCard';

interface AlertsProps {
  location: LocationInfo;
  warnings: MarineWarning[];
}

export const Alerts: React.FC<AlertsProps> = ({ location, warnings }) => {
  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16 pt-2">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-amber-50 text-amber-600">
              <AlertTriangle className="w-5 h-5" />
            </span>
            <h2 className="text-xl font-bold text-slate-800">
              Marine & Coastal Warnings System
            </h2>
          </div>
          <p className="text-xs text-slate-500">
            Real-time advisory feed from IMD Cyclone Warning Centre (CWC) and INCOIS Early Warning Systems for <strong className="text-slate-700">{location.name}</strong>.
          </p>
        </div>

        <div className="text-xs text-slate-500 text-right">
          <span className="px-3 py-1 rounded-full font-bold bg-amber-50 text-amber-800 border border-amber-200">
            {warnings.length} ACTIVE {warnings.length === 1 ? 'BULLETIN' : 'BULLETINS'}
          </span>
          <p className="text-[11px] text-slate-400 mt-1">Updated in real-time</p>
        </div>
      </div>

      {/* Main Warning List */}
      <WarningCard warnings={warnings} />

      {/* Guidelines Box */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 space-y-3">
        <h4 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 flex items-center gap-2">
          <Radio className="w-4 h-4 text-teal-600" />
          Standard Coastal Safety Advisory Protocols
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 space-y-1">
            <span className="font-bold text-emerald-800 block">🟢 Green Notice</span>
            <p className="text-slate-600 leading-snug">Normal sea state (&lt;1.5m waves). Motorized vessels and country boats can operate safely.</p>
          </div>
          <div className="p-4 rounded-2xl bg-amber-50/60 border border-amber-200 space-y-1">
            <span className="font-bold text-amber-800 block">🟡 Yellow Advisory</span>
            <p className="text-slate-600 leading-snug">Squally winds 40-50 kmph or wave height 1.5-2.5m. Deep-sea fishing vessels should exercise caution.</p>
          </div>
          <div className="p-4 rounded-2xl bg-rose-50/60 border border-rose-200 space-y-1">
            <span className="font-bold text-rose-800 block">🔴 Red Alert</span>
            <p className="text-slate-600 leading-snug">Severe storm / Cyclone track. Total prohibition of venturing into open sea waters.</p>
          </div>
        </div>
      </div>
    </div>
  );
};
