import re
from datetime import datetime
from typing import Dict, Any, List
from ..core.models import AgentEvent, UserType
from ..core.location import get_location, LOCATIONS

class PlannerAgent:
    """Planner Agent: Interprets user natural language, resolves location, and selects required agents."""
    
    @staticmethod
    def plan(message: str, user_type: UserType, location_id: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        msg_lower = message.lower()
        
        # 1. Resolve Location
        resolved_loc_id = location_id
        for loc_key, loc_info in LOCATIONS.items():
            if loc_key in msg_lower or loc_info.name.lower() in msg_lower:
                resolved_loc_id = loc_key
                break
                
        location_obj = get_location(resolved_loc_id)
        
        # 2. Extract Intent
        intent = "general_marine_inquiry"
        if any(w in msg_lower for w in ["fishing", "catch", "fish", "pfz", "zone"]):
            if any(w in msg_lower for w in ["safe", "can i", "permission", "should i", "go"]):
                intent = "fishing_safety"
            else:
                intent = "nearest_pfz"
        elif any(w in msg_lower for w in ["safe", "risk", "danger", "hazard", "can we sail"]):
            intent = "marine_safety"
        elif any(w in msg_lower for w in ["sst", "chlorophyll", "temperature", "salinity", "mld", "current"]):
            intent = "ocean_parameters"
        elif any(w in msg_lower for w in ["weather", "rain", "wind", "storm", "forecast"]):
            intent = "weather_inquiry"
        elif any(w in msg_lower for w in ["warning", "alert", "cyclone", "lightning"]):
            intent = "warning_check"
            
        # 3. Language detection (support for English, Telugu, Hindi, Tamil)
        language = "English"
        if any(re.search(r'[\u0c00-\u0c7f]', message) for _ in [1]):
            language = "Telugu"
        elif any(re.search(r'[\u0900-\u097f]', message) for _ in [1]):
            language = "Hindi"
        elif any(re.search(r'[\u0b80-\u0bff]', message) for _ in [1]):
            language = "Tamil"

        # 4. Decide required agents
        required_agents = ["weather", "ocean", "gis", "risk", "explanation"]
        if intent in ["fishing_safety", "nearest_pfz", "general_marine_inquiry"]:
            required_agents.insert(2, "pfz")
            
        event = AgentEvent(
            agent="Planner Agent",
            action=f"Analyzed query intent '{intent}' for {location_obj.name}",
            status="completed",
            details=f"Identified location: {location_obj.name} ({location_obj.coordinates.latitude}°N, {location_obj.coordinates.longitude}°E), target intent: {intent}, language: {language}, routing to: {', '.join(required_agents)}",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "intent": intent,
            "location_info": location_obj,
            "required_agents": required_agents,
            "language": language,
            "event": event
        }
