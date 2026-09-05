import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..core.models import AgentEvent, UserType, Coordinates, LocationInfo
from ..core.location import get_location, LOCATIONS

class PlannerAgent:
    """
    Planner Agent (Member 1 Lead):
    Interprets user natural language queries, resolves seaport locations and geo-coordinates,
    classifies maritime intent, detects language, and dynamically routes collaborative agent workflows.
    """
    
    @staticmethod
    def plan(message: str, user_type: UserType, location_id: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        # 1. Resolve Location & Geo-Coordinates
        resolved_loc_id = location_id
        extracted_coords: Optional[Coordinates] = None

        # Check for explicit lat/lon in message
        coord_pattern = re.search(r'([0-9]{1,2}\.[0-9]+)\s*°?\s*([nN])?\s*[,/ ]+\s*([0-9]{1,3}\.[0-9]+)\s*°?\s*([eE])?', message)
        if coord_pattern:
            try:
                lat = float(coord_pattern.group(1))
                lon = float(coord_pattern.group(3))
                if 5.0 <= lat <= 30.0 and 65.0 <= lon <= 95.0:
                    extracted_coords = Coordinates(latitude=lat, longitude=lon)
            except Exception:
                pass

        for loc_key, loc_info in LOCATIONS.items():
            if loc_key in msg_lower or loc_info.name.lower() in msg_lower:
                resolved_loc_id = loc_key
                break
                
        location_obj = get_location(resolved_loc_id)
        if extracted_coords:
            location_obj = LocationInfo(
                id="custom_coordinates",
                name=f"Custom Geo-Anchor ({extracted_coords.latitude:.2f}N, {extracted_coords.longitude:.2f}E)",
                state=location_obj.state,
                coordinates=extracted_coords,
                coastal_body=location_obj.coastal_body,
                port_type=location_obj.port_type,
                incois_zone_id=location_obj.incois_zone_id
            )
        
        # 2. Extract Intent
        intent = "general_marine_inquiry"
        if any(w in msg_lower for w in ["tide", "ebb", "flood", "high tide", "low tide", "spring tide", "neap"]):
            intent = "tide_inquiry"
        elif any(w in msg_lower for w in ["cyclone", "depression", "squall", "storm surge", "gale"]):
            intent = "cyclone_advisory"
        elif any(w in msg_lower for w in ["fishing", "catch", "fish", "pfz", "zone", "tuna", "mackerel"]):
            if any(w in msg_lower for w in ["safe", "can i", "permission", "should i", "go", "venture"]):
                intent = "fishing_safety"
            else:
                intent = "nearest_pfz"
        elif any(w in msg_lower for w in ["safe", "risk", "danger", "hazard", "can we sail", "operational"]):
            intent = "marine_safety"
        elif any(w in msg_lower for w in ["sst", "chlorophyll", "temperature", "salinity", "mld", "current", "thermocline"]):
            intent = "ocean_parameters"
        elif any(w in msg_lower for w in ["weather", "rain", "wind", "storm", "forecast", "visibility"]):
            intent = "weather_inquiry"
        elif any(w in msg_lower for w in ["warning", "alert", "bulletin", "lightning"]):
            intent = "warning_check"
        elif any(w in msg_lower for w in ["berth", "anchorage", "navigation", "harbour", "fairway"]):
            intent = "port_navigation"
            
        # 3. Multi-Lingual Detection
        language = "English"
        if re.search(r'[\u0c00-\u0c7f]', message):
            language = "Telugu"
        elif re.search(r'[\u0900-\u097f]', message):
            language = "Hindi"
        elif re.search(r'[\u0b80-\u0bff]', message):
            language = "Tamil"
        elif re.search(r'[\u0d00-\u0d7f]', message):
            language = "Malayalam"
        elif re.search(r'[\u0980-\u09ff]', message):
            language = "Bengali"
        elif re.search(r'[\u0a80-\u0aff]', message):
            language = "Gujarati"

        # 4. Formulate Execution Plan & Agent Routing
        required_agents = ["weather", "ocean", "gis", "risk", "explanation"]
        if intent in ["fishing_safety", "nearest_pfz", "general_marine_inquiry"]:
            required_agents.insert(2, "pfz")
            
        plan_summary = (
            f"1. Fetch live telemetry from Open-Meteo & IMD for {location_obj.name}\n"
            f"2. Pull ECMWF & Copernicus oceanographic physical parameters\n"
            f"3. Run Haversine & azimuth calculations for Potential Fishing Zones\n"
            f"4. Execute Ray-Casting GIS geofencing against marine protected areas\n"
            f"5. Compute deterministic multi-factor risk index score\n"
            f"6. Synthesize grounded marine advisory in {language} for role: {user_type}"
        )

        event = AgentEvent(
            agent="Planner Agent",
            action=f"Analyzed query intent '{intent}' for {location_obj.name}",
            status="completed",
            details=f"Identified location: {location_obj.name} ({location_obj.coordinates.latitude:.2f}°N, {location_obj.coordinates.longitude:.2f}°E), target intent: {intent}, language: {language}, routing: {', '.join(required_agents)}",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "intent": intent,
            "location_info": location_obj,
            "required_agents": required_agents,
            "language": language,
            "plan_summary": plan_summary,
            "event": event
        }
