import React from 'react';
import { Fish, Waves, Compass, AlertTriangle, ShieldCheck, Sparkles, Navigation } from 'lucide-react';
import { UserRole } from '../types';

interface QuickQuestionsProps {
  userRole: UserRole;
  locationName: string;
  onSelectPrompt: (prompt: string) => void;
}

export const QuickQuestions: React.FC<QuickQuestionsProps> = ({
  userRole,
  locationName,
  onSelectPrompt
}) => {
  const getPrompts = () => {
    switch (userRole) {
      case 'ocean_researcher':
        return [
          {
            icon: Waves,
            title: 'SST & Chlorophyll Gradient',
            prompt: `What are the current Sea Surface Temperature and Chlorophyll concentration levels near ${locationName}?`
          },
          {
            icon: Sparkles,
            title: 'Ocean Current & Swell Dynamics',
            prompt: `Analyze the surface current vectors and swell period near ${locationName}.`
          },
          {
            icon: Compass,
            title: 'Thermal Fronts & Mixed Layer Depth',
            prompt: `Where are the prominent oceanic fronts and what is the mixed layer depth near ${locationName}?`
          }
        ];
      case 'ship_operator':
        return [
          {
            icon: ShieldCheck,
            title: 'Maritime Route & Wave Risk',
            prompt: `Which nearby maritime corridor has lower sea state risk near ${locationName}?`
          },
          {
            icon: AlertTriangle,
            title: 'Squall & Gale Wind Alerts',
            prompt: `Are there any marine warnings, squalls, or cyclone alerts affecting ${locationName}?`
          },
          {
            icon: Navigation,
            title: 'Operational Sea Window',
            prompt: `What are tomorrow's wave and wind conditions for vessel transit near ${locationName}?`
          }
        ];
      default: // fisherman
        return [
          {
            icon: Fish,
            title: 'Can I go fishing tomorrow?',
            prompt: `Is it safe to go fishing tomorrow morning near ${locationName}?`
          },
          {
            icon: Compass,
            title: 'Nearest Potential Fishing Zone',
            prompt: `Where is the nearest Potential Fishing Zone (PFZ) from ${locationName}?`
          },
          {
            icon: AlertTriangle,
            title: 'Active Fishermen Warnings',
            prompt: `Are there any fishermen alerts or squally weather warnings along ${locationName} coast?`
          },
          {
            icon: Waves,
            title: 'Today Sea & Wave Conditions',
            prompt: `What are today's wave height and wind conditions near ${locationName}?`
          }
        ];
    }
  };

  const prompts = getPrompts();

  return (
    <div className="space-y-3 pt-2">
      <div className="flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-slate-500">
        <Sparkles className="w-3.5 h-3.5 text-teal-600" />
        <span>Quick Inquiries — {locationName}</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {prompts.map((p, idx) => {
          const Icon = p.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(p.prompt)}
              className="text-left p-3.5 rounded-2xl bg-white hover:bg-teal-50/50 border border-slate-200/90 hover:border-teal-400/60 shadow-sm hover:shadow-md transition-all flex items-start gap-3 group"
            >
              <div className="p-2 rounded-xl bg-teal-50 text-teal-600 group-hover:bg-teal-500 group-hover:text-white transition shrink-0 shadow-sm">
                <Icon className="w-4 h-4" />
              </div>
              <div className="min-w-0">
                <h4 className="text-xs font-bold text-slate-800 group-hover:text-teal-700 transition truncate">
                  {p.title}
                </h4>
                <p className="text-[11px] text-slate-500 truncate mt-0.5">
                  {p.prompt}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
