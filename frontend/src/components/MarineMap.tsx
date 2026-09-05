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
  Layers, 
  ShieldAlert, 
  Compass, 
  MessageSquarePlus,
  Anchor,
  Fish
} from 'lucide-react';
import { LocationInfo, PFZLocation } from '../types';
import { api } from '../services/api';

interface MarineMapProps {
  location: LocationInfo;
  pfzLocations?: PFZLocation[];
  selectedPfz?: PFZLocation | null;
  height?: string;
  showControls?: boolean;
  onAskAboutPfz?: (pfz: PFZLocation) => void;
}

// Custom Leaflet DivIcons
const createUserIcon = () =>
  L.divIcon({
    className: 'custom-user-marker',
    html: `<div style="background-color: #0d9488; width: 24px; height: 24px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 4px 12px rgba(13, 148, 136, 0.5); display: flex; align-items: center; justify-content: center;"><div style="width: 7px; height: 7px; background: white; border-radius: 50%;"></div></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });

const createPfzIcon = () =>
  L.divIcon({
    className: 'custom-pfz-marker',
    html: `<div style="background: #10b981; width: 28px; height: 28px; border-radius: 50%; border: 2.5px solid #ffffff; box-shadow: 0 4px 10px rgba(16, 185, 129, 0.4); display: flex; align-items: center; justify-content: center; color: white; font-size: 14px;">🐟</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  });

const createSelectedPfzIcon = () =>
  L.divIcon({
    className: 'custom-pfz-selected-marker',
    html: `<div style="background: #f59e0b; width: 34px; height: 34px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 6px 16px rgba(245, 158, 11, 0.5); display: flex; align-items: center; justify-content: center; color: white; font-size: 17px;">🎣</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17]
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
  height = '440px',
  showControls = true,
  onAskAboutPfz
}) => {
  const [showPfz, setShowPfz] = useState(true);
  const [showRiskZones, setShowRiskZones] = useState(true);
  const [showProtectedAreas, setShowProtectedAreas] = useState(true);
  const [gisData, setGisData] = useState<any>(null);

  const centerLat = location.coordinates.latitude;
  const centerLon = location.coordinates.longitude;

  // Fetch real backend GIS layers from Member 2 API
  useEffect(() => {
    let isMounted = true;
    api.getMapData(location.id)
      .then((data) => {
        if (isMounted) setGisData(data);
      })
      .catch((err) => console.warn('Could not load backend map layers:', err));
    return () => { isMounted = false; };
  }, [location.id]);

  // Fallback risk polygons around the selected port if backend polygons aren't rendered
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

  const protectedFeatures = gisData?.zones_layer?.features || [];

  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 shadow-inner overflow-hidden relative" style={{ height }}>
      {/* Map Layer Controls Bar */}
      {showControls && (
        <div className="absolute top-3 right-3 z-[1000] bg-white/95 backdrop-blur-md border border-slate-200 rounded-full px-3 py-1.5 shadow-lg flex flex-wrap items-center gap-3 text-xs">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider flex items-center gap-1">
            <Layers className="w-3.5 h-3.5 text-teal-600" /> Layers
          </span>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-700 hover:text-teal-700 font-medium">
            <input
              type="checkbox"
              checked={showPfz}
              onChange={(e) => setShowPfz(e.target.checked)}
              className="rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0 cursor-pointer"
            />
            <span>🐟 PFZ ({pfzLocations.length})</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-700 hover:text-teal-700 font-medium">
            <input
              type="checkbox"
              checked={showRiskZones}
              onChange={(e) => setShowRiskZones(e.target.checked)}
              className="rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0 cursor-pointer"
            />
            <span>🛡️ Risk Corridors</span>
          </label>
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-700 hover:text-teal-700 font-medium">
            <input
              type="checkbox"
              checked={showProtectedAreas}
              onChange={(e) => setShowProtectedAreas(e.target.checked)}
              className="rounded bg-slate-100 border-slate-300 text-teal-600 focus:ring-0 cursor-pointer"
            />
            <span>⛔ MPAs & Geofences</span>
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
            <div className="text-xs space-y-1.5 p-1 min-w-[200px]">
              <div className="flex items-center gap-1.5 font-bold text-slate-900 text-sm border-b pb-1">
                <Anchor className="w-4 h-4 text-teal-600" />
                <span>{location.name} Base Port</span>
              </div>
              <p className="text-slate-600">{location.state}, {location.coastal_body}</p>
              <div className="bg-slate-50 p-1.5 rounded font-mono text-[11px] text-teal-700 font-semibold">
                {centerLat.toFixed(4)}°N, {centerLon.toFixed(4)}°E
              </div>
              <p className="text-[10px] text-slate-400">Primary Marine Telemetry Operational Anchor</p>
            </div>
          </Popup>
        </Marker>

        {/* Maritime Risk Corridors */}
        {showRiskZones && (
          <>
            <Polygon
              positions={coastalPolygon}
              pathOptions={{
                color: '#10b981',
                fillColor: '#10b981',
                fillOpacity: 0.16,
                weight: 2,
                dashArray: '4, 4'
              }}
            >
              <Popup>
                <div className="text-xs space-y-1 p-1">
                  <p className="font-bold text-emerald-800 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Coastal Marine Corridor (Low Risk)
                  </p>
                  <p className="text-slate-700">Significant wave: 0.8 - 1.3 m | Wind: 3.5 - 5.2 m/s</p>
                  <p className="text-[10px] text-emerald-700 font-medium">Safe operating corridor for small motorized craft</p>
                </div>
              </Popup>
            </Polygon>

            <Polygon
              positions={offshorePolygon}
              pathOptions={{
                color: '#f59e0b',
                fillColor: '#f59e0b',
                fillOpacity: 0.15,
                weight: 2,
                dashArray: '4, 4'
              }}
            >
              <Popup>
                <div className="text-xs space-y-1 p-1">
                  <p className="font-bold text-amber-800 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-amber-500" />
                    Offshore Deep-Sea Sector (Moderate Risk)
                  </p>
                  <p className="text-slate-700">Significant wave: 1.5 - 2.2 m | Wind: 6.0 - 9.5 m/s</p>
                  <p className="text-[10px] text-amber-700 font-medium">Exercise vigilance beyond 15 nautical miles due to deep ocean swell</p>
                </div>
              </Popup>
            </Polygon>
          </>
        )}

        {/* INCOIS Potential Fishing Zones */}
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
                  <div className="text-xs space-y-2 p-1 max-w-[240px]">
                    <div className="flex items-center justify-between border-b pb-1">
                      <span className="font-bold text-emerald-800 flex items-center gap-1">
                        <Fish className="w-3.5 h-3.5 text-emerald-600" />
                        {pfz.id}
                      </span>
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                        INCOIS PFZ
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-slate-800 font-semibold">
                      <Compass className="w-3.5 h-3.5 text-teal-600" />
                      <span>{pfz.sector}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-1 text-[11px] text-slate-600 bg-slate-50 p-1.5 rounded">
                      <div>Distance: <strong>{pfz.distance_km} km</strong></div>
                      <div>Depth: <strong>{pfz.depth_m}m</strong></div>
                    </div>
                    {pfz.fish_species_likely && (
                      <p className="text-[10px] text-slate-700">
                        <strong>Species:</strong> {pfz.fish_species_likely.slice(0, 3).join(', ')}
                      </p>
                    )}
                    <p className="text-[10px] text-teal-800 font-mono font-semibold">
                      {pfz.latitude.toFixed(4)}°N, {pfz.longitude.toFixed(4)}°E
                    </p>

                    {onAskAboutPfz && (
                      <button
                        onClick={() => onAskAboutPfz(pfz)}
                        className="w-full mt-1.5 px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-[11px] flex items-center justify-center gap-1.5 transition shadow-sm"
                      >
                        <MessageSquarePlus className="w-3.5 h-3.5" />
                        <span>Ask AI About This Zone</span>
                      </button>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}

        {/* Marine Protected Areas & Restricted Geofences */}
        {showProtectedAreas && (
          <>
            {/* Coringa Mangrove Sanctuary buffer */}
            <Circle
              center={[16.85, 82.35]}
              radius={18000}
              pathOptions={{
                color: '#ef4444',
                fillColor: '#ef4444',
                fillOpacity: 0.12,
                weight: 2,
                dashArray: '3, 6'
              }}
            >
              <Popup>
                <div className="text-xs p-1 max-w-[220px]">
                  <p className="font-bold text-rose-800 flex items-center gap-1">
                    <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                    Coringa Mangrove Sanctuary
                  </p>
                  <p className="text-slate-600 text-[11px] mt-0.5">
                    Restricted trawling / Coastal sanctuary buffer zone (18 km radius).
                  </p>
                </div>
              </Popup>
            </Circle>

            {/* Gahirmatha Marine Sanctuary */}
            <Circle
              center={[20.72, 87.05]}
              radius={20000}
              pathOptions={{
                color: '#dc2626',
                fillColor: '#dc2626',
                fillOpacity: 0.12,
                weight: 2,
                dashArray: '3, 6'
              }}
            >
              <Popup>
                <div className="text-xs p-1 max-w-[220px]">
                  <p className="font-bold text-rose-800">Gahirmatha Marine Sanctuary</p>
                  <p className="text-slate-600 text-[11px]">
                    Olive Ridley turtle nesting sanctuary. Mechanized fishing prohibited.
                  </p>
                </div>
              </Popup>
            </Circle>
          </>
        )}
      </MapContainer>
    </div>
  );
};
