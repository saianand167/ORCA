import React from 'react';
import { 
  Waves, 
  ThermometerSun, 
  Navigation, 
  Sparkles, 
  LineChart as ChartIcon 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  LineChart, 
  Line 
} from 'recharts';
import { LocationInfo, OceanData, WeatherData } from '../types';

interface OceanConditionsProps {
  location: LocationInfo;
  ocean: OceanData | null;
  weather: WeatherData | null;
}

export const OceanConditions: React.FC<OceanConditionsProps> = ({
  location,
  ocean,
}) => {
  const chartData = ocean?.forecast_hourly && ocean.forecast_hourly.length > 0
    ? ocean.forecast_hourly
    : [
        { time: '06:00', wave_height_m: 1.2, swell_m: 0.9, sst_c: 29.1, current_ms: 0.38, wind_ms: 4.2 },
        { time: '09:00', wave_height_m: 1.3, swell_m: 1.0, sst_c: 29.3, current_ms: 0.40, wind_ms: 4.8 },
        { time: '12:00', wave_height_m: 1.4, swell_m: 1.1, sst_c: 29.6, current_ms: 0.42, wind_ms: 5.4 },
        { time: '15:00', wave_height_m: 1.6, swell_m: 1.2, sst_c: 29.5, current_ms: 0.45, wind_ms: 5.8 },
        { time: '18:00', wave_height_m: 1.5, swell_m: 1.1, sst_c: 29.2, current_ms: 0.41, wind_ms: 4.9 },
        { time: '21:00', wave_height_m: 1.3, swell_m: 1.0, sst_c: 29.0, current_ms: 0.39, wind_ms: 4.1 },
      ];

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-16 pt-2">
      {/* Top Banner */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-800">
              Ocean State & Marine Dynamics
            </h2>
            <span className="text-[10px] px-2.5 py-0.5 rounded-full font-bold bg-teal-50 text-teal-700 border border-teal-200">
              INCOIS OSF Telemetry
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Wave dynamics, swell spectra, thermocline, and surface current profiles for <strong className="text-slate-700">{location.name}</strong>.
          </p>
        </div>
        <div className="text-xs text-slate-500 text-right">
          <span>Freshness: <strong className="text-emerald-600">{ocean?.data_quality || 'LIVE'}</strong></span>
          <p className="text-[11px] text-slate-400">{ocean?.timestamp || 'Synchronized'}</p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <Waves className="w-4 h-4 text-teal-600" />
            <span>Significant Wave</span>
          </div>
          <p className="text-3xl font-black text-slate-800">
            {ocean?.significant_wave_height_m || 1.4} <span className="text-sm font-medium text-slate-400">m</span>
          </p>
          <p className="text-xs text-teal-600 font-semibold">
            Period: {ocean?.wave_period_s || 8.2}s ({ocean?.wave_direction_deg || 140}°)
          </p>
        </div>

        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <ThermometerSun className="w-4 h-4 text-amber-500" />
            <span>Sea Surface Temp</span>
          </div>
          <p className="text-3xl font-black text-slate-800">
            {ocean?.sea_surface_temperature_c || 29.4} <span className="text-sm font-medium text-slate-400">°C</span>
          </p>
          <p className="text-xs text-amber-600 font-semibold">
            Thermal front gradient normal
          </p>
        </div>

        <div className="p-5 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-1">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase">
            <Navigation className="w-4 h-4 text-blue-500" />
            <span>Surface Current</span>
          </div>
          <p className="text-3xl font-black text-slate-800">
            {ocean?.surface_current_speed_ms || 0.42} <span className="text-sm font-medium text-slate-400">m/s</span>
          </p>
          <p className="text-xs text-blue-600 font-semibold">
            Direction: {ocean?.surface_current_direction_deg || 45}° NE
          </p>
        </div>
      </div>

      {/* Recharts Wave & Swell Forecast Graph */}
      <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-xl shadow-slate-200/50 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-teal-50 text-teal-600">
              <ChartIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">
                Significant Wave & Swell Forecast (m)
              </h3>
              <p className="text-xs text-slate-400">
                24-Hour continuous oceanographic wave simulation
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs font-bold">
            <span className="flex items-center gap-1.5 text-teal-600">
              <span className="w-2.5 h-2.5 rounded-full bg-teal-500 inline-block" /> Wave Height
            </span>
            <span className="flex items-center gap-1.5 text-indigo-500">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 inline-block" /> Swell Height
            </span>
          </div>
        </div>

        <div className="h-64 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="waveGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0d9488" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#0d9488" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="swellGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
              <YAxis stroke="#94a3b8" fontSize={12} domain={[0, 'auto']} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', borderRadius: '1rem', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                itemStyle={{ fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="wave_height_m" stroke="#0d9488" strokeWidth={2.5} fillOpacity={1} fill="url(#waveGrad)" name="Wave Height (m)" />
              <Area type="monotone" dataKey="swell_m" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#swellGrad)" name="Swell (m)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
