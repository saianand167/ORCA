export type UserRole = 'fisherman' | 'ocean_researcher' | 'ship_operator';
export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'VERY HIGH';
export type DataQuality = 'LIVE' | 'CACHED' | 'DERIVED' | 'UNAVAILABLE' | 'DEMO SNAPSHOT' | 'DEMO / SIMULATED' | 'CONNECTOR READY — AUTH REQUIRED';

export interface LocationInfo {
  id: string;
  name: string;
  state: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  coastal_body: string;
  is_primary: boolean;
  description?: string;
}

export interface WeatherData {
  location: string;
  temperature_c?: number;
  humidity_percent?: number;
  rainfall_mm?: number;
  condition: string;
  wind_speed_ms: number;
  wind_speed_knots: number;
  wind_direction_deg: number;
  wind_direction_cardinal: string;
  visibility_km?: number;
  forecast_hourly?: Array<{
    time: string;
    temp_c: number;
    wind_ms: number;
  }>;
  source: string;
  data_quality: DataQuality;
  timestamp: string;
}

export interface OceanData {
  location: string;
  significant_wave_height_m: number;
  wave_period_s: number;
  wave_direction_deg: number;
  swell_height_m: number;
  swell_period_s: number;
  swell_direction_deg: number;
  surface_current_speed_ms: number;
  surface_current_direction_deg: number;
  sea_surface_temperature_c: number;
  mixed_layer_depth_m?: number;
  chlorophyll_mg_m3?: number;
  forecast_hourly?: Array<{
    time: string;
    wave_height_m: number;
    swell_m: number;
    sst_c: number;
    current_ms: number;
  }>;
  source: string;
  data_quality: DataQuality;
  timestamp: string;
}

export interface PFZLocation {
  id: string;
  sector: string;
  direction_bearing_deg: number;
  distance_km: number;
  distance_nm: number;
  depth_m: string;
  latitude: number;
  longitude: number;
  sst_range_c?: string;
  chlorophyll_gradient?: string;
  feature?: string;
  fish_species_likely: string[];
  recommended_gear?: string;
  safety_note?: string;
}

export interface PFZData {
  available: boolean;
  locations: PFZLocation[];
  nearest_pfz?: PFZLocation;
  advisory_date: string;
  valid_until: string;
  source: string;
  data_quality: DataQuality;
  landing_centre?: string;
  landing_centre_coords?: {
    latitude: number;
    longitude: number;
  };
}

export interface MarineWarning {
  id: string;
  category: string;
  severity: RiskLevel;
  headline: string;
  description: string;
  affected_areas: string[];
  color_code: string;
  issued_at: string;
  valid_until: string;
  source: string;
}

export interface RiskFactors {
  wave_score: number;
  wave_weight: number;
  wind_score: number;
  wind_weight: number;
  warning_score: number;
  warning_weight: number;
  current_score: number;
  current_weight: number;
}

export interface RiskAssessment {
  risk_level: RiskLevel;
  score: number;
  reasons: string[];
  safe_for_operations: boolean;
  summary: string;
  factor_breakdown?: RiskFactors;
  model_name: string;
  disclaimer: string;
}

export interface AgentEvent {
  agent: string;
  action: string;
  status: 'running' | 'completed' | 'fallback' | 'skipped' | 'error';
  details: string;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'orca';
  text: string;
  timestamp: string;
  risk?: RiskAssessment;
  weather?: WeatherData;
  ocean?: OceanData;
  pfz?: PFZData;
  warnings?: MarineWarning[];
  agent_activity?: AgentEvent[];
}

export interface SourceHealth {
  id: string;
  name: string;
  description: string;
  category: string;
  status: 'connected' | 'fallback' | 'credentials_required' | 'offline';
  data_quality: DataQuality;
  last_updated: string;
  endpoint_type: string;
  notes: string;
}
