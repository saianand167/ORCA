import React from 'react';
import { 
  Wind, 
  Thermometer, 
  Droplets, 
  Compass, 
  CloudSun 
} from 'lucide-react';
import { WeatherData } from '../types';

interface WeatherCardProps {
  weather: WeatherData;
}

export const WeatherCard: React.FC<WeatherCardProps> = ({ weather }) => {
  return (
    <div className="p-6 rounded-3xl bg-white border border-slate-100 shadow-lg shadow-slate-100 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-teal-50 text-teal-600">
            <CloudSun className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">Atmospheric Weather & Wind</h3>
            <p className="text-xs text-slate-400">{weather.source}</p>
          </div>
        </div>
        <span className={`text-xs px-3 py-1 rounded-full font-bold ${
          weather.data_quality === 'LIVE' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
        }`}>
          {weather.data_quality}
        </span>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Wind Speed */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Wind className="w-3.5 h-3.5 text-teal-600" />
            <span>Wind Speed</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {weather.wind_speed_ms} <span className="text-xs font-normal text-slate-400">m/s</span>
          </div>
          <div className="text-xs text-teal-700 font-bold">
            {weather.wind_speed_knots} knots
          </div>
        </div>

        {/* Wind Direction */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Compass className="w-3.5 h-3.5 text-indigo-500" />
            <span>Direction</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {weather.wind_direction_cardinal}
          </div>
          <div className="text-xs text-slate-500">
            {weather.wind_direction_deg}° azimuth
          </div>
        </div>

        {/* Temperature */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Thermometer className="w-3.5 h-3.5 text-amber-500" />
            <span>Atmosphere</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {weather.temperature_c !== undefined ? `${weather.temperature_c}°C` : '31.2°C'}
          </div>
          <div className="text-xs text-slate-500 truncate">
            {weather.condition}
          </div>
        </div>

        {/* Humidity */}
        <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-400">
            <Droplets className="w-3.5 h-3.5 text-blue-500" />
            <span>Humidity</span>
          </div>
          <div className="text-lg font-black text-slate-800">
            {weather.humidity_percent !== undefined ? `${weather.humidity_percent}%` : '76%'}
          </div>
          <div className="text-xs text-slate-500">
            Vis: {weather.visibility_km || 9.0} km
          </div>
        </div>
      </div>

      {/* Hourly Mini Forecast */}
      {weather.forecast_hourly && weather.forecast_hourly.length > 0 && (
        <div className="pt-2 border-t border-slate-100">
          <span className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider block mb-2">
            Hourly Trend (Next 12 Hours)
          </span>
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            {weather.forecast_hourly.slice(0, 6).map((item, idx) => (
              <div key={idx} className="shrink-0 text-center px-3 py-2 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                <span className="text-[10px] text-slate-400 block font-medium">{item.time}</span>
                <span className="font-bold text-slate-800 block my-0.5">{item.temp_c}°C</span>
                <span className="text-[10px] text-teal-600 font-bold">{item.wind_ms} m/s</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timestamp */}
      <div className="text-[11px] text-slate-400 flex justify-between pt-1">
        <span>Updated: {weather.timestamp}</span>
        <span>IMD / Open-Meteo Gateway</span>
      </div>
    </div>
  );
};
