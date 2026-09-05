import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { TabType } from './components/Sidebar';
import { BottomNav } from './components/BottomNav';
import { Home } from './pages/Home';
import { Assistant } from './pages/Assistant';
import { OceanConditions } from './pages/OceanConditions';
import { FishingZones } from './pages/FishingZones';
import { MapExplorer } from './pages/MapExplorer';
import { Alerts } from './pages/Alerts';
import { Sources } from './pages/Sources';
import { api } from './services/api';
import { 
  LocationInfo, 
  UserRole, 
  WeatherData, 
  OceanData, 
  PFZData, 
  MarineWarning, 
  RiskAssessment, 
  ChatMessage, 
  SourceHealth,
  PFZLocation
} from './types';

export const App: React.FC = () => {
  // State
  const [locations, setLocations] = useState<LocationInfo[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationInfo>({
    id: 'visakhapatnam',
    name: 'Visakhapatnam',
    state: 'Andhra Pradesh',
    coordinates: { latitude: 17.6868, longitude: 83.2185 },
    coastal_body: 'Bay of Bengal',
    is_primary: true
  });
  const [userRole, setUserRole] = useState<UserRole>('fisherman');
  const [activeTab, setActiveTab] = useState<TabType>('home');
  const [isDemoMode, setIsDemoMode] = useState<boolean>(false);

  // Marine Data State
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [ocean, setOcean] = useState<OceanData | null>(null);
  const [pfz, setPfz] = useState<PFZData | null>(null);
  const [warnings, setWarnings] = useState<MarineWarning[]>([]);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [sources, setSources] = useState<SourceHealth[]>([]);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [selectedPfzOnMap, setSelectedPfzOnMap] = useState<PFZLocation | null>(null);

  // Chat State
  const [conversationId, setConversationId] = useState<string>(`sess_${Date.now()}`);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState<boolean>(false);

  // Initial Load & Location Change
  useEffect(() => {
    async function loadData() {
      try {
        const locs = await api.getLocations();
        setLocations(locs);
        const initialLoc = locs.find((l) => l.is_primary) || locs[0] || selectedLocation;
        setSelectedLocation(initialLoc);
        await refreshMarineData(initialLoc.id, false);
        const srcs = await api.getSources();
        setSources(srcs);
        const sys = await api.getSystemStatus();
        setSystemStatus(sys);
      } catch (err) {
        console.error('Initialization error:', err);
      }
    }
    loadData();
  }, []);

  const refreshMarineData = async (locId: string, demo: boolean = isDemoMode) => {
    try {
      const [wData, oData, pData, warnData, riskData] = await Promise.all([
        api.getWeather(locId, demo),
        api.getOcean(locId, demo),
        api.getPFZ(locId),
        api.getWarnings(locId, demo),
        api.getRisk(locId, userRole, demo).catch(() => null)
      ]);
      setWeather(wData);
      setOcean(oData);
      setPfz(pData);
      setWarnings(warnData);

      if (riskData) {
        setRisk(riskData);
      } else {
        // Fallback baseline evaluation if offline
        const waveH = oData.significant_wave_height_m || 1.3;
        const windMs = wData.wind_speed_ms || 4.5;
        const score = Math.min(100, Math.round(waveH * 18 + windMs * 3 + (warnData.length > 0 ? 10 : 0)));
        const level = score > 60 ? 'HIGH' : score > 30 ? 'MODERATE' : 'LOW';

        setRisk({
          risk_level: level,
          score: score,
          reasons: [
            `Significant Wave Height: ${waveH} m (${waveH < 1.5 ? 'Calm to moderate' : 'Elevated'})`,
            `Surface Wind Speed: ${windMs} m/s (${wData.wind_direction_cardinal || 'SE'})`,
            warnData.length > 0 ? warnData[0].headline : 'No severe coastal warning active'
          ],
          safe_for_operations: score <= 60,
          summary: score <= 30 ? 'Favorable conditions across coastal corridors.' : 'Moderate conditions; monitor offshore swell.',
          model_name: 'ORCA Prototype Risk Model',
          disclaimer: 'Prototype decision-support result. Always verify official marine advisories before operating.'
        });
      }

      // Populate initial greeting if messages empty
      if (messages.length === 0) {
        setMessages([
          {
            id: 'init_welcome',
            sender: 'orca',
            text: `Welcome to **ORCA** Marine Intelligence for **${selectedLocation.name}**.\n\nI correlate INCOIS Ocean State Forecasts, IMD coastal bulletins, and Potential Fishing Zones (PFZ) for **${userRole.replace('_', ' ')}s**.\n\nHow can I assist your voyage or research today?`,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            weather: wData,
            ocean: oData,
            pfz: pData
          }
        ]);
      }
    } catch (err) {
      console.error('Failed to load marine telemetry:', err);
    }
  };

  const handleToggleDemoMode = async (val: boolean) => {
    setIsDemoMode(val);
    await refreshMarineData(selectedLocation.id, val);
  };

  const handleSelectLocation = async (loc: LocationInfo) => {
    setSelectedLocation(loc);
    await refreshMarineData(loc.id, isDemoMode);
  };

  const handleSendMessage = async (text: string) => {
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsChatLoading(true);

    try {
      const resp = await api.sendChatMessage({
        message: text,
        location_id: selectedLocation.id,
        latitude: selectedLocation.coordinates.latitude,
        longitude: selectedLocation.coordinates.longitude,
        user_type: userRole,
        conversation_id: conversationId,
        demo_mode: isDemoMode
      });

      const orcaMsg: ChatMessage = {
        id: `orca_${Date.now()}`,
        sender: 'orca',
        text: resp.answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        risk: resp.risk,
        weather: resp.weather,
        ocean: resp.ocean,
        pfz: resp.pfz,
        warnings: resp.warnings,
        agent_activity: resp.agent_activity
      };

      setMessages((prev) => [...prev, orcaMsg]);
      if (resp.risk) setRisk(resp.risk);
      if (resp.weather) setWeather(resp.weather);
      if (resp.ocean) setOcean(resp.ocean);
      if (resp.pfz) setPfz(resp.pfz);
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: `err_${Date.now()}`,
        sender: 'orca',
        text: `I encountered an issue connecting to the multi-agent backend. Please ensure the FastAPI server is running on port 8000.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const handlePromptClick = (prompt: string) => {
    setActiveTab('assistant');
    handleSendMessage(prompt);
  };

  const handleAskAboutPfz = (p: PFZLocation) => {
    setActiveTab('assistant');
    handleSendMessage(`Provide navigational safety, wave conditions, and catch recommendations for zone ${p.id} (${p.distance_km}km, bearing ${p.sector}).`);
  };

  return (
    <div className="min-h-screen text-slate-800 flex flex-col antialiased">
      {/* Top Header */}
      <Header
        locations={locations}
        selectedLocation={selectedLocation}
        onSelectLocation={handleSelectLocation}
        userRole={userRole}
        onChangeUserRole={setUserRole}
        dataQuality={weather?.data_quality || (isDemoMode ? 'DEMO / SIMULATED' : 'LIVE')}
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        isDemoMode={isDemoMode}
        onToggleDemoMode={handleToggleDemoMode}
      />

      {/* Demo Simulation Alert Banner */}
      {isDemoMode && (
        <div className="bg-gradient-to-r from-amber-500 via-amber-600 to-red-600 text-white font-medium px-4 py-2.5 text-center text-xs sm:text-sm flex flex-wrap items-center justify-center gap-2 shadow-md">
          <span className="font-extrabold uppercase px-2 py-0.5 bg-black/25 text-amber-100 rounded text-[11px] tracking-wider border border-white/20">
            Demo / Simulation Mode Active
          </span>
          <span className="text-white/95">
            Simulating severe cyclonic squall conditions (18.5 m/s winds, 4.2m swells, Red Warning). All telemetry is synthetic for ISRO SIH jury demonstration.
          </span>
          <button
            onClick={() => handleToggleDemoMode(false)}
            className="ml-2 px-2.5 py-0.5 rounded bg-white text-slate-900 font-bold hover:bg-slate-100 transition shadow-xs text-xs cursor-pointer"
          >
            Switch to Live Telemetry
          </button>
        </div>
      )}

      {/* Main App Content Area */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <main className="w-full">
          {activeTab === 'home' && (
            <Home
              location={selectedLocation}
              userRole={userRole}
              weather={weather}
              ocean={ocean}
              pfz={pfz}
              warnings={warnings}
              risk={risk}
              onSelectPrompt={handlePromptClick}
              onNavigateTab={setActiveTab}
              onSelectPfzOnMap={(p) => setSelectedPfzOnMap(p)}
            />
          )}

          {activeTab === 'assistant' && (
            <Assistant
              location={selectedLocation}
              userRole={userRole}
              messages={messages}
              isLoading={isChatLoading}
              onSendMessage={handleSendMessage}
              onResetChat={() => {
                setConversationId(`sess_${Date.now()}`);
                setMessages([]);
              }}
              weather={weather}
              ocean={ocean}
              pfz={pfz}
              risk={risk}
            />
          )}

          {activeTab === 'ocean' && (
            <OceanConditions
              location={selectedLocation}
              ocean={ocean}
              weather={weather}
            />
          )}

          {activeTab === 'pfz' && (
            <FishingZones
              location={selectedLocation}
              pfz={pfz}
              onSelectPfzOnMap={(p) => {
                setSelectedPfzOnMap(p);
                setActiveTab('map');
              }}
            />
          )}

          {activeTab === 'map' && (
            <MapExplorer
              locations={locations}
              selectedLocation={selectedLocation}
              onSelectLocation={handleSelectLocation}
              pfz={pfz}
              userRole={userRole}
              selectedPfz={selectedPfzOnMap}
              onAskAboutPfz={handleAskAboutPfz}
            />
          )}

          {activeTab === 'alerts' && (
            <Alerts
              location={selectedLocation}
              warnings={warnings}
            />
          )}

          {activeTab === 'sources' && (
            <Sources
              sources={sources}
              systemStatus={systemStatus}
            />
          )}
        </main>
      </div>

      {/* Mobile Bottom Navigation */}
      <BottomNav
        activeTab={activeTab}
        onChangeTab={setActiveTab}
        warningCount={warnings.length}
      />
    </div>
  );
};

export default App;
