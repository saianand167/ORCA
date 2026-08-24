import React, { useState } from 'react';
import { 
  Fish, 
  MapPin, 
  Compass, 
  Anchor, 
  ExternalLink 
} from 'lucide-react';
import { LocationInfo, PFZData, PFZLocation } from '../types';
import { MarineMap } from '../components/MarineMap';

interface FishingZonesProps {
  location: LocationInfo;
  pfz: PFZData | null;
  onSelectPfzOnMap?: (pfz: PFZLocation) => void;
}

export const FishingZones: React.FC<FishingZonesProps> = ({
  location,
  pfz,
  onSelectPfzOnMap
}) => {
  const [selectedPfz, setSelectedPfz] = useState<PFZLocation | null>(
    pfz?.nearest_pfz || (pfz?.locations && pfz.locations.length > 0 ? pfz.locations[0] : null)
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16 pt-2">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <Fish className="w-5 h-5" />
            </span>
            <h2 className="text-xl font-bold text-slate-800">
              INCOIS Potential Fishing Zones (PFZ) Advisory
            </h2>
          </div>
          <p className="text-xs text-slate-500">
            Satellite Ocean Colour (OCM) and SST thermal gradient aggregation for <strong className="text-slate-700">{location.name}</strong>.
          </p>
        </div>

        <div className="text-xs text-slate-500 text-right">
          <span className="px-3 py-1 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
            {pfz?.locations.length || 0} ZONES ACTIVE
          </span>
          <p className="text-[11px] text-slate-400 mt-1">Valid: {pfz?.valid_until || 'Current Advisory'}</p>
        </div>
      </div>

      {/* Grid: Zone List & Map Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Zone Cards (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <h3 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-teal-600" /> Active Advisories from Landing Centre
          </h3>

          {pfz?.locations.map((item) => {
            const isSelected = selectedPfz?.id === item.id;
            return (
              <div
                key={item.id}
                onClick={() => {
                  setSelectedPfz(item);
                  if (onSelectPfzOnMap) onSelectPfzOnMap(item);
                }}
                className={`p-5 rounded-3xl border cursor-pointer transition space-y-2.5 ${
                  isSelected
                    ? 'bg-emerald-50/60 border-emerald-400 shadow-md shadow-emerald-500/10'
                    : 'bg-white border-slate-100 shadow-sm hover:border-slate-300 hover:shadow-md'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-black px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                      {item.id}
                    </span>
                    <span className="text-xs font-bold text-slate-700">{item.sector}</span>
                  </div>
                  <span className="text-xs font-black text-emerald-700">
                    {item.distance_km} km <span className="text-[10px] text-slate-400 font-normal">({item.distance_nm} nm)</span>
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-slate-600">
                  <div>Depth: <strong className="text-slate-800">{item.depth_m} m</strong></div>
                  <div>SST: <strong className="text-slate-800">{item.sst_range_c || '28.8 - 29.4°C'}</strong></div>
                </div>

                {item.fish_species_likely && item.fish_species_likely.length > 0 && (
                  <div className="flex flex-wrap gap-1 pt-1">
                    {item.fish_species_likely.map((sp, idx) => (
                      <span key={idx} className="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 font-medium">
                        {sp}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right: Map View (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50">
            <h4 className="text-xs font-bold text-slate-700 mb-3 flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-teal-600" />
              Spatial PFZ Locations & Bearing Overlay
            </h4>
            <MarineMap
              location={location}
              pfzLocations={pfz?.locations || []}
              selectedPfz={selectedPfz}
              height="440px"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
