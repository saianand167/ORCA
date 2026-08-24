import React from 'react';
import { Database, CheckCircle2, AlertCircle, Clock, Key } from 'lucide-react';
import { SourceHealth } from '../types';

interface SourceCardProps {
  source: SourceHealth;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const getStatusBadge = () => {
    switch (source.status) {
      case 'connected':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Connected
          </span>
        );
      case 'credentials_required':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-full bg-amber-50 text-amber-700 border border-amber-200">
            <Key className="w-3.5 h-3.5" />
            Auth Optional
          </span>
        );
      case 'fallback':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-full bg-teal-50 text-teal-700 border border-teal-200">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Active Gateway
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold rounded-full bg-rose-50 text-rose-700 border border-rose-200">
            <AlertCircle className="w-3.5 h-3.5" />
            Offline
          </span>
        );
    }
  };

  return (
    <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-md shadow-slate-100 space-y-3.5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-teal-50 text-teal-600">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-800">{source.name}</h4>
            <span className="text-xs text-teal-600 font-semibold">{source.category}</span>
          </div>
        </div>
        {getStatusBadge()}
      </div>

      <p className="text-xs text-slate-600 leading-relaxed">
        {source.description}
      </p>

      <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 text-xs space-y-1">
        <div className="flex justify-between text-slate-500">
          <span>Endpoint Method:</span>
          <span className="font-mono text-slate-800 font-semibold">{source.endpoint_type}</span>
        </div>
        <div className="flex justify-between text-slate-500">
          <span>Telemetry Quality:</span>
          <span className="font-bold text-emerald-700">{source.data_quality}</span>
        </div>
      </div>

      {source.notes && (
        <p className="text-xs text-slate-400 italic">
          Note: {source.notes}
        </p>
      )}

      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
        <span>Verified Telemetry Layer</span>
        <span className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {source.last_updated}
        </span>
      </div>
    </div>
  );
};
