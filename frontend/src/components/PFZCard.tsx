import React from 'react';
import { 
  Fish, 
  MapPin, 
  Compass, 
  Anchor, 
  ExternalLink, 
  Calendar 
} from 'lucide-react';
import { PFZData, PFZLocation } from '../types';

interface PFZCardProps {
  pfz: PFZData;
  onViewOnMap?: (location?: PFZLocation) => void;
}

export const PFZCard: React.FC<PFZCardProps> = ({ pfz, onViewOnMap }) => {
  const nearest = pfz.nearest_pfz;

  return (
    <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-emerald-50 text-emerald-600">
            <Fish className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">Potential Fishing Zones (PFZ)</h3>
            <p className="text-xs text-slate-400">{pfz.source}</p>
          </div>
        </div>
        <span className={`text-xs px-3 py-1 rounded-full font-bold ${
          pfz.available ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
        }`}>
          {pfz.available ? `${pfz.locations.length} ZONES ACTIVE` : 'UNAVAILABLE'}
        </span>
      </div>

      {/* Nearest Zone Hero Box */}
      {nearest && (
        <div className="p-5 rounded-3xl bg-emerald-50/50 border border-emerald-200/80 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-emerald-200/80 text-emerald-900">
                NEAREST PFZ
              </span>
              <span className="text-sm font-black text-slate-800">{nearest.id}</span>
            </div>
            {onViewOnMap && (
              <button
                onClick={() => onViewOnMap(nearest)}
                className="flex items-center gap-1 text-xs text-emerald-700 hover:text-emerald-900 font-bold transition"
              >
                <span>View on Map</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="space-y-0.5">
              <span className="text-slate-500 font-medium">Distance</span>
              <p className="text-sm font-black text-slate-800">
                {nearest.distance_km} km <span className="text-[10px] text-slate-400 font-normal">({nearest.distance_nm} nm)</span>
              </p>
            </div>
            <div className="space-y-0.5">
              <span className="text-slate-500 font-medium">Bearing Sector</span>
              <p className="text-sm font-black text-slate-800">{nearest.sector}</p>
            </div>
            <div className="space-y-0.5">
              <span className="text-slate-500 font-medium">Depth Contour</span>
              <p className="text-sm font-black text-slate-800">{nearest.depth_m} m</p>
            </div>
            <div className="space-y-0.5">
              <span className="text-slate-500 font-medium">Chlorophyll</span>
              <p className="text-sm font-black text-emerald-700 truncate">Thermal Front</p>
            </div>
          </div>

          {/* Likely Species */}
          {nearest.fish_species_likely && nearest.fish_species_likely.length > 0 && (
            <div className="pt-2 border-t border-emerald-200/60 flex flex-wrap items-center gap-1.5 text-xs">
              <span className="text-slate-500 text-[11px] font-medium">Likely Aggregation:</span>
              {nearest.fish_species_likely.map((sp, idx) => (
                <span key={idx} className="px-2.5 py-0.5 rounded-full bg-white text-slate-700 text-[11px] font-semibold border border-emerald-200">
                  {sp}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Advisory Dates and Landing Centre */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-500 pt-1">
        <div className="flex items-center gap-2">
          <Anchor className="w-3.5 h-3.5 text-teal-600" />
          <span>Landing Centre: <strong className="text-slate-700">{pfz.landing_centre || 'Visakhapatnam'}</strong></span>
        </div>
        <div className="flex items-center gap-2 sm:justify-end">
          <Calendar className="w-3.5 h-3.5 text-teal-600" />
          <span>Valid Until: <strong className="text-slate-700">{pfz.valid_until || 'Active'}</strong></span>
        </div>
      </div>
    </div>
  );
};
