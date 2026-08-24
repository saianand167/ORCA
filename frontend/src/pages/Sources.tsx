import React from 'react';
import { Database } from 'lucide-react';
import { SourceHealth } from '../types';
import { SourceCard } from '../components/SourceCard';

interface SourcesProps {
  sources: SourceHealth[];
  systemStatus: any;
}

export const Sources: React.FC<SourcesProps> = ({ sources, systemStatus }) => {
  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16 pt-2">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-teal-50 text-teal-600">
              <Database className="w-5 h-5" />
            </span>
            <h2 className="text-xl font-bold text-slate-800">
              Data Connectors & System Architecture
            </h2>
          </div>
          <p className="text-xs text-slate-500">
            Real-time status of official Indian marine institutions, satellite Earth observation pipelines, and AI orchestrators.
          </p>
        </div>

        <div className="text-xs text-slate-500 text-right">
          <span className="px-3 py-1 rounded-full font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
            SYSTEM STATUS: {systemStatus?.status || 'OPERATIONAL'}
          </span>
          <p className="text-[11px] text-slate-400 mt-1">Version {systemStatus?.version || '1.0.0'}</p>
        </div>
      </div>

      {/* Overview Stat Counters */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-md shadow-slate-100 space-y-1">
          <span className="text-xs font-bold text-slate-400 uppercase">Connectors</span>
          <p className="text-3xl font-black text-slate-800">{sources.length}</p>
        </div>
        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-md shadow-slate-100 space-y-1">
          <span className="text-xs font-bold text-slate-400 uppercase">Connected</span>
          <p className="text-3xl font-black text-emerald-600">
            {sources.filter((s) => s.status === 'connected').length}
          </p>
        </div>
        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-md shadow-slate-100 space-y-1">
          <span className="text-xs font-bold text-slate-400 uppercase">Fallback Gateways</span>
          <p className="text-3xl font-black text-teal-600">
            {sources.filter((s) => s.status === 'fallback').length}
          </p>
        </div>
        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-md shadow-slate-100 space-y-1">
          <span className="text-xs font-bold text-slate-400 uppercase">Store</span>
          <p className="text-sm font-extrabold text-slate-700 mt-2">SQLite Active</p>
        </div>
      </div>

      {/* Connectors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sources.map((src) => (
          <SourceCard key={src.id} source={src} />
        ))}
      </div>
    </div>
  );
};
