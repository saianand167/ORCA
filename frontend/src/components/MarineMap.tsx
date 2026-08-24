import React, { useState, useEffect } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  Marker, 
  Popup, 
  Polygon, 
  Circle, 
  useMap 
} from 'react-leaflet';
import L from 'leaflet';
import { 
  Layers 
} from 'lucide-react';
import { LocationInfo, PFZLocation } from '../types';

interface MarineMapProps {
  location: LocationInfo;
  pfzLocations?: PFZLocation[];
  selectedPfz?: PFZLocation | null;
  height?: string;
  showControls?: boolean;
}

// Custom Leaflet Icons using SVGs
const createUserIcon = () =>
  L.divIcon({
    className: 'custom-user-marker',
    html: `<div style="background-color: #0d9488; width: 22px; height: 22px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 4px 12px rgba(13, 148, 136, 0.4); display: flex; align-items: center; justify-content: center;"><div style="width: 6px; height: 6px; background: white; border-radius: 50%;"></div></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11]
  });

const createPfzIcon = () =>
  L.divIcon({
    className: 'custom-pfz-marker',
    html: `<div style="background: #10b981; width: 26px; height: 26px; border-radius: 50%; border: 2.5px solid #ffffff; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; color: white; font-size: 13px;">🐟</div>`,
    iconSize: [26, 26],
    iconAnchor: [13, 13]
  });

const createSelectedPfzIcon = () =>
  L.divIcon({
    className: 'custom-pfz-selected-marker',
    html: `<div style="background: #f59e0b; width: 32px; height: 32px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 6px 16px rgba(245, 158, 11, 0.45); display: flex; align-items: center; justify-content: center; color: white; font-size: 16px;">🎣</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });

function MapRecenter({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lon], 9, { animate: true });
  }, [lat, lon, map]);
  return null;
}

export const MarineMap: React.FC<MarineMapProps> = ({
  location,
  pfzLocations = [],
  selectedPfz = null,
  height = '420px',
  showControls = true
}) => {
  const [showPfz, setShowPfz] = useState(true);
  const [showRiskZones, setShowRiskZones] = useState(true);
  const [showProtectedAreas, setShowProtectedAreas] = useState(true);

  const centerLat = location.coordinates.latitude;
  const centerLon = location.coordinates.longitude;

  // Approximate risk polygons around the selected port
  const coastalPolygon: [number, number][] = [
    [centerLat, centerLon],
    [centerLat - 0.15, centerLon + 0.35],
    [centerLat + 0.25, centerLon + 0.45],
    [centerLat + 0.35, centerLon + 0.1],
  ];

  const offshorePolygon: [number, number][] = [
    [centerLat - 0.15, centerLon + 0.35],
    [centerLat - 0.35, centerLon + 0.85],
    [centerLat + 0.45, centerLon + 0.95],
    [centerLat + 0.25, centerLon + 0.45],
  ];

  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 shadow-inner overflow-hidden relative" style={{ height }}>
      {/* Map Layer Controls Bar */}
      {showControls && (
        <div className="absolute top-3 right-3 z-[1000] bg-white/90 backdrop-blur-md border border-slate-200 rounded-full px-3 py-1.5 shadow-md flex flex-wrap items-center gap-3 text-xs">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-teal-600" /> Layers
          </span>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-700 hover:text-teal-700 font-medium">
            <input
              type="checkbox"
              checked={showPfz}
              onChange={(e) => setShowPfz(e.target.checked)}
              className="rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0"
            />
            <span>🐟 PFZ</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-700 hover:text-teal-700 font-medium">
            <input
              type="checkbox"
              checked={showRiskZones}
              onChange={(e) => setShowRiskZones(e.target.checked)}
              className="rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0"
            />
            <span>🛡️ Risk</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-700 hover:text-teal-700 font-medium">
            <input
              type="checkbox"
              checked={showProtectedAreas}
              onChange={(e) => setShowProtectedAreas(e.target.checked)}
              className="rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0"
            />
            <span>⛔ MPAs</span>
          </label>
        </div>
      )}

      {/* Map Container */}
      <MapContainer
        center={[centerLat, centerLon]}
        zoom={9}
        scrollWheelZoom={false}
        style={{ width: '100%', height: '100%' }}
      >
        <MapRecenter lat={centerLat} lon={centerLon} />

        {/* Clean Voyager Basemap Tile Layer */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* User Port Location Marker */}
        <Marker position={[centerLat, centerLon]} icon={createUserIcon()}>
          <Popup>
            <div className="text-xs space-y-1 p-1">
              <p className="font-bold text-slate-900 text-sm">{location.name} Port</p>
              <p className="text-slate-600">{location.state}, {location.coastal_body}</p>
              <p className="font-mono text-[11px] text-teal-700 font-semibold">
                {centerLat.toFixed(4)}°N, {centerLon.toFixed(4)}°E
              </p>
              <p className="text-[10px] text-slate-400">Base Marine Operational Centre</p>
            </div>
          </Popup>
        </Marker>

        {/* Risk Zones Polygons */}
        {showRiskZones && (
          <>
            <Polygon
              positions={coastalPolygon}
              pathOptions={{
                color: '#10b981',
                fillColor: '#10b981',
                fillOpacity: 0.18,
                weight: 2,
                dashArray: '4, 4'
              }}
            >
              <Popup>
                <div className="text-xs space-y-1 p-1">
                  <p className="font-bold text-emerald-800">Coastal Corridor (Low Risk)</p>
                  <p className="text-slate-700">Significant wave: 0.9 - 1.3 m | Wind: 3.5 - 5.0 m/s</p>
                  <p className="text-[10px] text-slate-500">Favorable corridor for small craft</p>
                </div>
              </Popup>
            </Polygon>

            <Polygon
              positions={offshorePolygon}
              pathOptions={{
                color: '#f59e0b',
                fillColor: '#f59e0b',
                fillOpacity: 0.16,
                weight: 2,
                dashArray: '4, 4'
              }}
            >
              <Popup>
                <div className="text-xs space-y-1 p-1">
                  <p className="font-bold text-amber-800">Offshore Deep Sector (Moderate Risk)</p>
                  <p className="text-slate-700">Significant wave: 1.5 - 2.2 m | Swell: 1.2 m</p>
                  <p className="text-[10px] text-slate-500">Exercise vigilance beyond 15 nautical miles</p>
                </div>
              </Popup>
            </Polygon>
          </>
        )}

        {/* Potential Fishing Zones */}
        {showPfz &&
          pfzLocations.map((pfz) => {
            const isSelected = selectedPfz?.id === pfz.id;
            return (
              <Marker
                key={pfz.id}
                position={[pfz.latitude, pfz.longitude]}
                icon={isSelected ? createSelectedPfzIcon() : createPfzIcon()}
              >
                <Popup>
                  <div className="text-xs space-y-1.5 p-1 max-w-[220px]">
                    <div className="flex items-center justify-between border-b pb-1">
                      <span className="font-bold text-emerald-700">{pfz.id}</span>
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1 rounded font-semibold">
                        INCOIS PFZ
                      </span>
                    </div>
                    <p className="text-slate-800 font-semibold">{pfz.sector}</p>
                    <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600">
                      <div>Dist: <strong>{pfz.distance_km} km</strong></div>
                      <div>Depth: <strong>{pfz.depth_m}m</strong></div>
                    </div>
                    {pfz.fish_species_likely && (
                      <p className="text-[10px] text-slate-600">
                        Species: {pfz.fish_species_likely.slice(0, 3).join(', ')}
                      </p>
                    )}
                    <p className="text-[10px] text-teal-800 font-mono font-semibold">
                      {pfz.latitude.toFixed(4)}°N, {pfz.longitude.toFixed(4)}°E
                    </p>
                  </div>
                </Popup>
              </Marker>
            );
          })}

        {/* Marine Protected Area Example */}
        {showProtectedAreas && (
          <Circle
            center={[centerLat + 0.15, centerLon - 0.25]}
            radius={8000}
            pathOptions={{
              color: '#ef4444',
              fillColor: '#ef4444',
              fillOpacity: 0.15,
              weight: 2,
              dashArray: '3, 6'
            }}
          >
            <Popup>
              <div className="text-xs p-1">
                <p className="font-bold text-rose-800">Ecological Buffer Zone</p>
                <p className="text-slate-600 text-[11px]">Restricted bottom trawling / Conservation area</p>
              </div>
            </Popup>
          </Circle>
        )}
      </MapContainer>
    </div>
  );
};
