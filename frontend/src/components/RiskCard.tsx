import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Waves, 
  Wind, 
  Compass, 
  Info 
} from 'lucide-react';
import { RiskAssessment } from '../types';

interface RiskCardProps {
  risk: RiskAssessment;
}

export const RiskCard: React.FC<RiskCardProps> = ({ risk }) => {
  const getRiskColor = () => {
    switch (risk.risk_level) {
      case 'LOW':
        return {
          bg: 'from-emerald-950/40 via-slate-900/80 to-navy-900',
          border: 'border-emerald-500/30',
          text: 'text-emerald-400',
          badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          bar: 'bg-emerald-400',
          icon: ShieldCheck
        };
      case 'MODERATE':
        return {
          bg: 'from-amber-950/30 via-slate-900/80 to-navy-900',
          border: 'border-amber-500/30',
          text: 'text-amber-400',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          bar: 'bg-amber-400',
          icon: AlertTriangle
        };
      case 'HIGH':
        return {
          bg: 'from-orange-950/40 via-slate-900/80 to-navy-900',
          border: 'border-orange-500/40',
          text: 'text-orange-400',
          badge: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
          bar: 'bg-orange-500',
          icon: ShieldAlert
        };
      default:
        return {
          bg: 'from-rose-950/40 via-slate-900/80 to-navy-900',
          border: 'border-rose-500/40',
          text: 'text-rose-400',
          badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
          bar: 'bg-rose-500',
          icon: ShieldAlert
        };
    }
  };

  const style = getRiskColor();
  const Icon = style.icon;

  return (
    <div className={`p-6 rounded-2xl bg-gradient-to-br ${style.bg} border ${style.border} shadow-xl relative overflow-hidden`}>
      {/* Background radial glow */}
      <div className="absolute top-0 right-0 -mr-16 -mt-16 w-64 h-64 rounded-full bg-cyan-500/5 blur-3xl pointer-events-none" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        {/* Left: Score and Status */}
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Marine Operational Risk Engine
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {risk.model_name}
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="p-3.5 rounded-2xl bg-slate-800/80 border border-slate-700/60 shadow-inner">
              <Icon className={`w-8 h-8 ${style.text}`} />
            </div>
            <div>
              <div className="flex items-center gap-3">
                <span className={`text-2xl lg:text-3xl font-extrabold ${style.text} tracking-tight`}>
                  {risk.risk_level} RISK
                </span>
                <span className={`text-xs font-bold px-2.5 py-1 rounded-full border ${style.badge}`}>
                  {risk.score} / 100
                </span>
              </div>
              <p className="text-sm text-slate-300 mt-0.5">
                {risk.summary}
              </p>
            </div>
          </div>
        </div>

        {/* Right: Key Factors */}
        <div className="md:max-w-md w-full space-y-2.5 bg-slate-950/40 p-4 rounded-xl border border-slate-800/80">
          <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
            <Info className="w-3.5 h-3.5 text-cyan-400" />
            Key Risk Drivers Evaluated:
          </span>
          <div className="space-y-1.5">
            {risk.reasons.map((reason, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="text-cyan-400 font-bold">•</span>
                <span>{reason}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Progress Risk Bar */}
      <div className="mt-5 space-y-1.5">
        <div className="flex justify-between text-[11px] text-slate-400 font-medium">
          <span>0 (Calm)</span>
          <span>30 (Low)</span>
          <span>60 (Moderate)</span>
          <span>80 (High)</span>
          <span>100 (Severe)</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden relative">
          <div
            className={`h-full ${style.bar} transition-all duration-500 rounded-full`}
            style={{ width: `${Math.max(5, Math.min(100, risk.score))}%` }}
          />
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
        <span>{risk.disclaimer}</span>
        <span className="font-medium text-slate-300">Prototype Decision Support</span>
      </div>
    </div>
  );
};
