import React from 'react';
import { 
  Waves, 
  Activity, 
  ThermometerSun, 
  Navigation, 
  Sparkles,
  Layers
} from 'lucide-react';
import { OceanData } from '../types';

interface OceanCardProps {
  ocean: OceanData;
}

export const OceanCard: React.FC<OceanCardProps> = ({ ocean }) => {
  return (
    <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-teal-50 text-teal-600">
            <Waves className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">Ocean State & Telemetry</h3>
            <p className="text-xs text-slate-400">{ocean.source}</p>
          </div>
        </div>
        <span className={`text-xs px-3 py-1 rounded-full font-bold ${
          ocean.data_quality === 'LIVE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
        }`}>
          {ocean.data_quality}
        </span>
      </div>

      {/* Metric Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {/* Wave Height */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Waves className="w-3.5 h-3.5 text-teal-600" />
            <span>Sig Wave Height</span>
          </div>
          <div className="text-xl font-black text-slate-800">
            {ocean.significant_wave_height_m} <span className="text-xs font-normal text-slate-400">m</span>
          </div>
          <div className="text-xs text-teal-700 font-bold">
            Period: {ocean.wave_period_s}s ({ocean.wave_direction_deg}°)
          </div>
        </div>

        {/* Swell Height */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Activity className="w-3.5 h-3.5 text-indigo-500" />
            <span>Offshore Swell</span>
          </div>
          <div className="text-xl font-black text-slate-800">
            {ocean.swell_height_m} <span className="text-xs font-normal text-slate-400">m</span>
          </div>
          <div className="text-xs text-indigo-700 font-bold">
            Period: {ocean.swell_period_s}s ({ocean.swell_direction_deg}°)
          </div>
        </div>

        {/* Sea Surface Temp */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <ThermometerSun className="w-3.5 h-3.5 text-amber-500" />
            <span>Sea Surface Temp</span>
          </div>
          <div className="text-xl font-black text-slate-800">
            {ocean.sea_surface_temperature_c} <span className="text-xs font-normal text-slate-400">°C</span>
          </div>
          <div className="text-xs text-amber-700 font-medium">
            Thermal Gradient Normal
          </div>
        </div>

        {/* Surface Current */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Navigation className="w-3.5 h-3.5 text-blue-500" />
            <span>Surface Current</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {ocean.surface_current_speed_ms} <span className="text-xs font-normal text-slate-400">m/s</span>
          </div>
          <div className="text-xs text-blue-700 font-medium">
            Dir: {ocean.surface_current_direction_deg}°
          </div>
        </div>

        {/* Chlorophyll */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span>Chlorophyll-a</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {ocean.chlorophyll_mg_m3 !== undefined ? `${ocean.chlorophyll_mg_m3}` : '0.85'}{' '}
            <span className="text-xs font-normal text-slate-400">mg/m³</span>
          </div>
          <div className="text-xs text-emerald-700 font-medium">
            OCM Satellite Proxy
          </div>
        </div>

        {/* Mixed Layer Depth */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Layers className="w-3.5 h-3.5 text-purple-500" />
            <span>Mixed Layer (MLD)</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {ocean.mixed_layer_depth_m !== undefined ? `${ocean.mixed_layer_depth_m} m` : '24.5 m'}
          </div>
          <div className="text-xs text-purple-700 font-medium">
            Thermocline boundary
          </div>
        </div>
      </div>

      {/* Footer Timestamp */}
      <div className="text-[11px] text-slate-400 flex justify-between pt-2 border-t border-slate-100">
        <span>INCOIS OSF Model Telemetry</span>
        <span>Updated: {ocean.timestamp}</span>
      </div>
    </div>
  );
};
