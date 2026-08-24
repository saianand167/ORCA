import React from 'react';
import { 
  Bot, 
  Sparkles 
} from 'lucide-react';
import { 
  ChatMessage, 
  LocationInfo, 
  UserRole, 
  WeatherData, 
  OceanData, 
  PFZData, 
  RiskAssessment 
} from '../types';
import { ChatPanel } from '../components/ChatPanel';
import { QuickQuestions } from '../components/QuickQuestions';

interface AssistantProps {
  location: LocationInfo;
  userRole: UserRole;
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (msg: string) => void;
  onResetChat?: () => void;
  weather: WeatherData | null;
  ocean: OceanData | null;
  pfz: PFZData | null;
  risk: RiskAssessment | null;
}

export const Assistant: React.FC<AssistantProps> = ({
  location,
  userRole,
  messages,
  isLoading,
  onSendMessage,
  onResetChat,
  risk
}) => {
  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16 pt-2">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-teal-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">
              ORCA Multi-Agent Conversational Assistant
            </h2>
            <p className="text-xs text-slate-500">
              Active Port: <span className="text-teal-700 font-bold">{location.name}</span> | Role: <span className="text-slate-700 capitalize font-medium">{userRole.replace('_', ' ')}</span>
            </p>
          </div>
        </div>

        {risk && (
          <div className="flex items-center gap-2 self-start sm:self-auto px-4 py-2 rounded-full bg-slate-50 border border-slate-200 text-xs">
            <span className="text-slate-500 font-medium">Active Risk:</span>
            <span className={`font-black ${
              risk.risk_level === 'LOW' ? 'text-emerald-600' : risk.risk_level === 'MODERATE' ? 'text-teal-600' : 'text-rose-600'
            }`}>
              {risk.risk_level} ({risk.score}/100)
            </span>
          </div>
        )}
      </div>

      {/* Role Prompt Suggestions */}
      <QuickQuestions
        userRole={userRole}
        locationName={location.name}
        onSelectPrompt={onSendMessage}
      />

      {/* Main Chat Interface */}
      <ChatPanel
        location={location}
        userRole={userRole}
        messages={messages}
        isLoading={isLoading}
        onSendMessage={onSendMessage}
        onResetChat={onResetChat}
      />
    </div>
  );
};
