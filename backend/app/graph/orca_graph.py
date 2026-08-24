from typing import Dict, Any, List, TypedDict
from ..core.models import (
    UserType, WeatherData, OceanData, PFZData, MarineWarning,
    RiskAssessment, AgentEvent, ChatResponse
)
from ..agents.planner import PlannerAgent
from ..agents.weather_agent import WeatherAgent
from ..agents.ocean_agent import OceanAgent
from ..agents.pfz_agent import PFZAgent
from ..agents.gis_agent import GISAgent
from ..agents.risk_agent import RiskAgent
from ..agents.explanation_agent import ExplanationAgent
from ..database.database import get_conversation_history, save_chat_turn

class AgentState(TypedDict):
    message: str
    user_type: UserType
    location_id: str
    latitude: float
    longitude: float
    conversation_id: str
    language: str
    required_agents: List[str]
    weather: WeatherData
    ocean: OceanData
    pfz: PFZData
    warnings: List[MarineWarning]
    gis_alerts: List[Dict[str, Any]]
    risk: RiskAssessment
    answer: str
    agent_activity: List[AgentEvent]

class ORCAGraphOrchestrator:
    """Orchestrates collaborative agents across Planner -> Data Connectors -> GIS -> Risk -> Explanation."""

    @staticmethod
    async def run(
        message: str,
        user_type: UserType = "fisherman",
        location_id: str = "visakhapatnam",
        latitude: float = 17.6868,
        longitude: float = 83.2185,
        conversation_id: str = "session_default"
    ) -> ChatResponse:
        
        agent_activity: List[AgentEvent] = []
        history = get_conversation_history(conversation_id, limit=6)

        # 1. PLANNER AGENT
        plan_res = PlannerAgent.plan(message, user_type, location_id, history)
        agent_activity.append(plan_res["event"])
        
        loc_info = plan_res["location_info"]
        target_lat = loc_info.coordinates.latitude
        target_lon = loc_info.coordinates.longitude
        loc_name = loc_info.name
        language = plan_res["language"]

        # 2. DATA AGENTS (Weather, Ocean, PFZ, GIS)
        weather_res = await WeatherAgent.execute(target_lat, target_lon, loc_name)
        agent_activity.append(weather_res["event"])
        weather = weather_res["weather"]
        warnings = weather_res["warnings"]

        ocean_res = await OceanAgent.execute(target_lat, target_lon, loc_name)
        agent_activity.append(ocean_res["event"])
        ocean = ocean_res["ocean"]

        pfz_res = await PFZAgent.execute(target_lat, target_lon, loc_name)
        agent_activity.append(pfz_res["event"])
        pfz = pfz_res["pfz"]

        gis_res = GISAgent.execute(target_lat, target_lon, loc_name)
        agent_activity.append(gis_res["event"])
        gis_alerts = gis_res["gis_alerts"]

        # 3. RISK AGENT
        risk_res = RiskAgent.execute(weather, ocean, warnings, user_type)
        agent_activity.append(risk_res["event"])
        risk = risk_res["risk"]

        # 4. EXPLANATION AGENT
        exp_res = await ExplanationAgent.generate_explanation(
            user_message=message,
            user_type=user_type,
            language=language,
            location_name=loc_name,
            risk=risk,
            weather=weather,
            ocean=ocean,
            pfz=pfz,
            warnings=warnings,
            gis_alerts=gis_alerts,
            conversation_history=history
        )
        agent_activity.append(exp_res["event"])
        answer = exp_res["answer"]

        # Sources summary
        sources = [
            {"name": "INCOIS Ocean State Forecast", "type": "Oceanographic Telemetry", "status": ocean.data_quality, "timestamp": ocean.timestamp},
            {"name": "INCOIS Marine Fisheries Advisory", "type": "PFZ Advisory", "status": pfz.data_quality, "timestamp": pfz.advisory_date},
            {"name": "IMD Coastal Bulletin", "type": "Meteorological Warning", "status": weather.data_quality, "timestamp": weather.timestamp},
            {"name": "Open-Meteo Global Marine", "type": "Wave & Atmospheric API", "status": "LIVE", "timestamp": "Real-time"}
        ]

        response = ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            language_detected=language,
            risk=risk,
            weather=weather,
            ocean=ocean,
            pfz=pfz,
            warnings=warnings,
            gis_alerts=gis_alerts,
            sources=sources,
            agent_activity=agent_activity
        )

        # Save to database session
        save_chat_turn(conversation_id, user_type, loc_info.id, message, response.model_dump())

        return response
