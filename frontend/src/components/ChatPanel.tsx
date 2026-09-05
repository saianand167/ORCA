import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  Compass, 
  RotateCcw,
  Waves,
  Fish,
  Cpu
} from 'lucide-react';
import { ChatMessage, LocationInfo, UserRole } from '../types';
import { AgentActivity } from './AgentActivity';

interface ChatPanelProps {
  location: LocationInfo;
  userRole: UserRole;
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  onResetChat?: () => void;
}

const AGENT_STAGES = [
  { agent: 'Planner Agent', desc: 'Resolving query intent & marine geo-coordinates...', icon: '🧭' },
  { agent: 'Weather & Ocean Agents', desc: 'Ingesting live Open-Meteo & ECMWF marine telemetry...', icon: '🌊' },
  { agent: 'PFZ & GIS Agents', desc: 'Computing Haversine bearings & MPA geofences...', icon: '🐟' },
  { agent: 'Deterministic Risk Engine', desc: 'Evaluating multi-factor marine safety index...', icon: '🛡️' },
  { agent: 'Explanation Agent', desc: 'Synthesizing grounded multi-lingual advisory...', icon: '🤖' },
];

export const ChatPanel: React.FC<ChatPanelProps> = ({
  location,
  userRole,
  messages,
  isLoading,
  onSendMessage,
  onResetChat
}) => {
  const [inputText, setInputText] = useState('');
  const [activeStageIdx, setActiveStageIdx] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, activeStageIdx]);

  // Cycle through live agent stages while waiting for response
  useEffect(() => {
    if (!isLoading) {
      setActiveStageIdx(0);
      return;
    }
    const interval = setInterval(() => {
      setActiveStageIdx((prev) => (prev < AGENT_STAGES.length - 1 ? prev + 1 : prev));
    }, 1800);
    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText('');
  };

  return (
    <div className="flex flex-col h-[650px] rounded-3xl bg-white border border-slate-200 shadow-xl shadow-slate-200/50 overflow-hidden">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-teal-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-800">Ask ORCA Marine Assistant</h3>
              <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-teal-100 text-teal-800 border border-teal-200">
                Multi-Agent AI
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Synthesizing INCOIS & IMD live telemetry for <strong className="text-slate-700">{location.name}</strong>
            </p>
          </div>
        </div>

        {onResetChat && (
          <button
            onClick={onResetChat}
            className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 bg-white hover:bg-slate-100 border border-slate-200 rounded-full font-semibold transition cursor-pointer"
            title="Reset conversation"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset</span>
          </button>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 bg-[#fafcfa]">
        {messages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
            >
              {!isUser && (
                <div className="w-9 h-9 rounded-2xl bg-teal-500 text-white shrink-0 flex items-center justify-center mt-1 shadow-md shadow-teal-500/20">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] sm:max-w-[78%] rounded-2xl p-4 sm:p-5 text-sm leading-relaxed space-y-3 ${
                  isUser
                    ? 'bg-teal-600 text-white rounded-tr-none shadow-md shadow-teal-600/20'
                    : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-md shadow-slate-200/40'
                }`}
              >
                {/* Agent Activity Trace */}
                {!isUser && msg.agent_activity && msg.agent_activity.length > 0 && (
                  <AgentActivity events={msg.agent_activity} defaultExpanded={false} />
                )}

                {/* Risk Badge Header */}
                {!isUser && msg.risk && (
                  <div className="flex items-center justify-between gap-2 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-600">Operational Risk:</span>
                      <span
                        className={`px-2.5 py-0.5 rounded-full font-black ${
                          msg.risk.risk_level === 'LOW'
                            ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                            : msg.risk.risk_level === 'MODERATE'
                            ? 'bg-amber-100 text-amber-800 border border-amber-300'
                            : 'bg-rose-100 text-rose-800 border border-rose-300'
                        }`}
                      >
                        {msg.risk.risk_level} ({msg.risk.score}/100)
                      </span>
                    </div>
                    <span className="text-[11px] font-semibold text-slate-500">
                      {msg.risk.safe_for_operations ? '✅ Operations Feasible' : '⚠️ Extreme Caution'}
                    </span>
                  </div>
                )}

                {/* Markdown Text */}
                <div className="whitespace-pre-line text-xs sm:text-sm leading-relaxed">
                  {msg.text}
                </div>

                {/* Telemetry Chips */}
                {!isUser && (msg.weather || msg.ocean || msg.pfz) && (
                  <div className="pt-2 border-t border-slate-100 flex flex-wrap gap-2 text-[11px]">
                    {msg.ocean && (
                      <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium">
                        <Waves className="w-3 h-3 text-teal-600" /> Wave: {msg.ocean.significant_wave_height_m}m
                      </span>
                    )}
                    {msg.weather && (
                      <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium">
                        <Compass className="w-3 h-3 text-teal-600" /> Wind: {msg.weather.wind_speed_ms}m/s ({msg.weather.wind_direction_cardinal})
                      </span>
                    )}
                    {msg.pfz && msg.pfz.nearest_pfz && (
                      <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 font-medium border border-emerald-200">
                        <Fish className="w-3 h-3 text-emerald-600" /> Nearest PFZ: {msg.pfz.nearest_pfz.distance_km}km
                      </span>
                    )}
                  </div>
                )}

                {/* Timestamp */}
                <div className={`text-[10px] text-right ${isUser ? 'text-teal-100' : 'text-slate-400'}`}>
                  {msg.timestamp}
                </div>
              </div>

              {isUser && (
                <div className="w-9 h-9 rounded-2xl bg-slate-200 text-slate-700 shrink-0 flex items-center justify-center mt-1 shadow-sm font-bold text-xs">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          );
        })}

        {/* Live Multi-Agent Execution Progress Card */}
        {isLoading && (
          <div className="flex gap-3 justify-start items-start">
            <div className="w-9 h-9 rounded-2xl bg-teal-500 text-white shrink-0 flex items-center justify-center shadow-md animate-pulse mt-1">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-4 rounded-2xl rounded-tl-none bg-white border border-teal-200 text-xs text-slate-700 shadow-lg max-w-[85%] sm:max-w-[70%] space-y-3">
              <div className="flex items-center justify-between gap-2 border-b border-slate-100 pb-2">
                <span className="font-extrabold text-teal-800 flex items-center gap-1.5">
                  <Cpu className="w-4 h-4 text-teal-600 animate-spin" />
                  ORCA Multi-Agent Orchestrator Active
                </span>
                <span className="text-[10px] bg-teal-100 text-teal-800 px-2 py-0.5 rounded-full font-bold">
                  Step {activeStageIdx + 1} of {AGENT_STAGES.length}
                </span>
              </div>

              {/* Active Step Highlight */}
              <div className="p-2.5 rounded-xl bg-teal-50/70 border border-teal-100 flex items-center gap-3">
                <span className="text-xl">{AGENT_STAGES[activeStageIdx].icon}</span>
                <div>
                  <div className="font-bold text-teal-900 text-[11px]">
                    {AGENT_STAGES[activeStageIdx].agent}
                  </div>
                  <div className="text-[11px] text-slate-600">
                    {AGENT_STAGES[activeStageIdx].desc}
                  </div>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div 
                  className="bg-teal-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${((activeStageIdx + 1) / AGENT_STAGES.length) * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSend} className="p-4 bg-white border-t border-slate-100 flex items-center gap-3">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={`Ask ORCA about fishing safety, waves, or weather near ${location.name}...`}
          disabled={isLoading}
          className="flex-1 bg-slate-100 text-sm text-slate-800 placeholder-slate-400 px-5 py-3 rounded-full border border-slate-200 focus:outline-none focus:border-teal-500 focus:bg-white transition"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isLoading}
          className="p-3 bg-teal-500 hover:bg-teal-600 text-white rounded-full font-medium disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-teal-500/25 transition flex items-center justify-center shrink-0 cursor-pointer"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
};
