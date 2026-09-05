import React from 'react';
import { 
  Map as MapIcon, 
  Layers, 
  MapPin 
} from 'lucide-react';
import { LocationInfo, PFZData, PFZLocation, UserRole } from '../types';
import { MarineMap } from '../components/MarineMap';

interface MapExplorerProps {
  locations: LocationInfo[];
  selectedLocation: LocationInfo;
  onSelectLocation: (loc: LocationInfo) => void;
  pfz: PFZData | null;
  userRole: UserRole;
  selectedPfz?: PFZLocation | null;
  onAskAboutPfz?: (pfz: PFZLocation) => void;
}

export const MapExplorer: React.FC<MapExplorerProps> = ({
  locations,
  selectedLocation,
  onSelectLocation,
  pfz,
  selectedPfz,
  onAskAboutPfz
}) => {
  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16 pt-2">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-teal-50 text-teal-600">
              <MapIcon className="w-5 h-5" />
            </div>
            <h2 className="text-xl font-bold text-slate-800">
              Interactive Marine Geospatial Explorer
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Visualizing bathymetry, Potential Fishing Zones, maritime risk corridors & Marine Protected Areas.
          </p>
        </div>

        {/* Location Dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Target Port:</span>
          <select
            value={selectedLocation.id}
            onChange={(e) => {
              const found = locations.find((l) => l.id === e.target.value);
              if (found) onSelectLocation(found);
            }}
            className="bg-slate-100 text-xs font-bold text-slate-800 border border-slate-200 rounded-full px-4 py-2 focus:outline-none focus:border-teal-500 cursor-pointer"
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id} className="bg-white text-slate-800">
                {loc.name} ({loc.state})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Full GIS Map View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-8 p-3 bg-white rounded-3xl border border-slate-100 shadow-xl shadow-slate-200/50">
          <MarineMap
            location={selectedLocation}
            pfzLocations={pfz?.locations || []}
            selectedPfz={selectedPfz}
            height="560px"
            onAskAboutPfz={onAskAboutPfz}
          />
        </div>

        {/* Right Info Drawer */}
        <div className="lg:col-span-4 space-y-4">
          {/* Legend Card */}
          <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-slate-700 flex items-center gap-2">
              <Layers className="w-4 h-4 text-teal-600" />
              Map Layer Legend
            </h3>
            <div className="space-y-3 text-xs text-slate-600">
              <div className="flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 rounded-full bg-teal-500 shadow-sm" />
                <span>Base Port Anchor ({selectedLocation.name})</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 shadow-sm" />
                <span>INCOIS Potential Fishing Zone (PFZ)</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 rounded bg-emerald-100 border border-emerald-400" />
                <span>Low-Risk Coastal Corridor (&lt; 1.3m waves)</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 rounded bg-amber-100 border border-amber-400" />
                <span>Moderate-Risk Deep Sea Sector (&gt; 1.5m waves)</span>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="w-3.5 h-3.5 rounded-full bg-rose-100 border border-rose-400" />
                <span>Marine Protected Area / Ecological Reserve</span>
              </div>
            </div>
          </div>

          {/* Spatial Reference */}
          <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-3 text-xs">
            <h4 className="font-bold text-slate-800 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-teal-600" />
              Spatial Telemetry Reference
            </h4>
            <div className="space-y-2 text-slate-600">
              <div className="flex justify-between">
                <span className="text-slate-400">Latitude:</span>
                <span className="font-mono text-teal-700 font-bold">{selectedLocation.coordinates.latitude}° N</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Longitude:</span>
                <span className="font-mono text-teal-700 font-bold">{selectedLocation.coordinates.longitude}° E</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Basin:</span>
                <span className="font-semibold text-slate-800">{selectedLocation.coastal_body}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
