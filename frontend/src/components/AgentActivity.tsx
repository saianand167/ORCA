import React, { useState } from 'react';
import { 
  Cpu, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Clock, 
  AlertCircle 
} from 'lucide-react';
import { AgentEvent } from '../types';

interface AgentActivityProps {
  events: AgentEvent[];
  defaultExpanded?: boolean;
}

export const AgentActivity: React.FC<AgentActivityProps> = ({ events, defaultExpanded = true }) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!events || events.length === 0) return null;

  return (
    <div className="rounded-2xl bg-slate-50 border border-slate-200 shadow-sm overflow-hidden text-xs my-2">
      {/* Header Bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2.5 flex items-center justify-between bg-slate-100/80 hover:bg-slate-200/60 transition"
      >
        <div className="flex items-center gap-2">
          <div className="p-1 rounded-lg bg-teal-500/15 text-teal-700">
            <Cpu className="w-3.5 h-3.5" />
          </div>
          <span className="font-bold text-slate-800">ORCA Multi-Agent Execution Trace</span>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-teal-100 text-teal-800 border border-teal-200">
            {events.length} Agents Collaborated
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-slate-500">
          <span className="text-[11px] font-medium">{isExpanded ? 'Hide Trace' : 'View Reasoning'}</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Waterfall Steps */}
      {isExpanded && (
        <div className="p-3.5 space-y-2 border-t border-slate-200 bg-white">
          {events.map((evt, idx) => {
            const isCompleted = evt.status === 'completed';
            const isFallback = evt.status === 'fallback';
            return (
              <div key={idx} className="flex items-start gap-2.5">
                {/* Timeline node */}
                <div className="mt-0.5 shrink-0 flex flex-col items-center">
                  {isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  ) : isFallback ? (
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500" />
                  ) : (
                    <Clock className="w-3.5 h-3.5 text-teal-600 animate-spin" />
                  )}
                  {idx < events.length - 1 && (
                    <div className="w-0.5 h-4 bg-slate-200 my-0.5" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold text-slate-800 text-[11px]">
                      {evt.agent}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {evt.timestamp}
                    </span>
                  </div>
                  <p className="text-slate-600 text-[11px] leading-snug mt-0.5">
                    {evt.action}
                  </p>
                  {evt.details && (
                    <p className="text-[10px] text-teal-700 font-mono mt-0.5 truncate bg-teal-50/50 p-1 rounded">
                      {evt.details}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
