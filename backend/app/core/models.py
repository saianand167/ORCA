from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

UserType = Literal["fisherman", "ocean_researcher", "ship_operator"]
RiskLevel = Literal["LOW", "MODERATE", "HIGH", "VERY HIGH"]
DataQuality = Literal["LIVE", "CACHED", "DEMO SNAPSHOT"]

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class LocationInfo(BaseModel):
    id: str
    name: str
    state: str
    coordinates: Coordinates
    coastal_body: str = "Bay of Bengal"
    is_primary: bool = False
    description: Optional[str] = None

class WeatherData(BaseModel):
    location: str
    temperature_c: Optional[float] = None
    humidity_percent: Optional[float] = None
    rainfall_mm: Optional[float] = None
    condition: str = "Clear"
    wind_speed_ms: float = 0.0
    wind_speed_knots: float = 0.0
    wind_direction_deg: float = 0.0
    wind_direction_cardinal: str = "N"
    visibility_km: Optional[float] = 10.0
    forecast_hourly: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = "Open-Meteo / IMD"
    data_quality: DataQuality = "LIVE"
    timestamp: str = ""

class OceanData(BaseModel):
    location: str
    significant_wave_height_m: float = 0.0
    wave_period_s: float = 0.0
    wave_direction_deg: float = 0.0
    swell_height_m: float = 0.0
    swell_period_s: float = 0.0
    swell_direction_deg: float = 0.0
    surface_current_speed_ms: float = 0.0
    surface_current_direction_deg: float = 0.0
    sea_surface_temperature_c: float = 0.0
    mixed_layer_depth_m: Optional[float] = None
    chlorophyll_mg_m3: Optional[float] = None
    forecast_hourly: List[Dict[str, Any]] = Field(default_factory=list)
    source: str = "INCOIS Ocean State Forecast / Marine Telemetry"
    data_quality: DataQuality = "LIVE"
    timestamp: str = ""

class PFZLocation(BaseModel):
    id: str
    sector: str
    direction_bearing_deg: float
    distance_km: float
    distance_nm: float
    depth_m: str
    latitude: float
    longitude: float
    sst_range_c: Optional[str] = None
    chlorophyll_gradient: Optional[str] = None
    feature: Optional[str] = None
    fish_species_likely: List[str] = Field(default_factory=list)
    recommended_gear: Optional[str] = None
    safety_note: Optional[str] = None

class PFZData(BaseModel):
    available: bool = True
    locations: List[PFZLocation] = Field(default_factory=list)
    nearest_pfz: Optional[PFZLocation] = None
    advisory_date: str = ""
    valid_until: str = ""
    source: str = "INCOIS Marine Fisheries Advisory"
    data_quality: DataQuality = "DEMO SNAPSHOT"
    landing_centre: str = ""
    landing_centre_coords: Optional[Coordinates] = None

class MarineWarning(BaseModel):
    id: str
    category: str
    severity: RiskLevel
    headline: str
    description: str
    affected_areas: List[str] = Field(default_factory=list)
    color_code: str = "YELLOW"
    issued_at: str = ""
    valid_until: str = ""
    source: str = "IMD / INCOIS"

class RiskAssessment(BaseModel):
    risk_level: RiskLevel = "LOW"
    score: int = 15
    reasons: List[str] = Field(default_factory=list)
    safe_for_operations: bool = True
    summary: str = ""
    model_name: str = "ORCA Prototype Risk Model"
    disclaimer: str = "Prototype decision-support result. Always verify official marine advisories before operating."

class AgentEvent(BaseModel):
    agent: str
    action: str
    status: Literal["running", "completed", "fallback", "skipped", "error"] = "completed"
    details: str = ""
    timestamp: str = ""

class ChatRequest(BaseModel):
    message: str
    location_id: Optional[str] = "visakhapatnam"
    latitude: Optional[float] = 17.6868
    longitude: Optional[float] = 83.2185
    user_type: UserType = "fisherman"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    language_detected: str = "English"
    risk: RiskAssessment
    weather: WeatherData
    ocean: OceanData
    pfz: PFZData
    warnings: List[MarineWarning] = Field(default_factory=list)
    gis_alerts: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    agent_activity: List[AgentEvent] = Field(default_factory=list)
    disclaimer: str = "ORCA is a prototype decision-support system. Marine conditions can change rapidly. Always verify official marine and navigation advisories."

class SourceHealth(BaseModel):
    id: str
    name: str
    description: str
    category: str
    status: Literal["connected", "fallback", "credentials_required", "offline"]
    data_quality: DataQuality
    last_updated: str
    endpoint_type: str
    notes: str
