from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

from ..core.models import (
    UserType, WeatherData, OceanData, PFZData, MarineWarning,
    RiskAssessment, AgentEvent, ChatResponse, LocationInfo
)
from ..agents.planner import PlannerAgent
from ..agents.weather_agent import WeatherAgent
from ..agents.ocean_agent import OceanAgent
from ..agents.pfz_agent import PFZAgent
from ..agents.gis_agent import GISAgent
from ..agents.risk_agent import RiskAgent
from ..agents.explanation_agent import ExplanationAgent
from ..database.database import get_conversation_history, save_chat_turn

class AgentState(TypedDict, total=False):
    message: str
    user_type: UserType
    location_id: str
    location_info: LocationInfo
    target_lat: float
    target_lon: float
    loc_name: str
    conversation_id: str
    language: str
    intent: str
    required_agents: List[str]
    plan_summary: str
    history: List[Dict[str, Any]]
    demo_mode: bool
    weather: WeatherData
    ocean: OceanData
    pfz: PFZData
    warnings: List[MarineWarning]
    gis_alerts: List[Dict[str, Any]]
    risk: RiskAssessment
    answer: str
    agent_activity: List[AgentEvent]

# --- LangGraph Node Functions ---

def planner_node(state: AgentState) -> Dict[str, Any]:
    history = state.get("history", [])
    plan_res = PlannerAgent.plan(
        state["message"],
        state["user_type"],
        state.get("location_id", "visakhapatnam"),
        history
    )
    loc_info = plan_res["location_info"]
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(plan_res["event"])
    
    return {
        "location_info": loc_info,
        "target_lat": loc_info.coordinates.latitude,
        "target_lon": loc_info.coordinates.longitude,
        "loc_name": loc_info.name,
        "intent": plan_res["intent"],
        "required_agents": plan_res["required_agents"],
        "language": plan_res["language"],
        "plan_summary": plan_res.get("plan_summary", ""),
        "agent_activity": current_activity
    }

async def weather_node(state: AgentState) -> Dict[str, Any]:
    if state.get("demo_mode"):
        from datetime import datetime
        from ..api.weather import get_weather
        from ..api.warnings import get_warnings
        loc_id = state.get("location_id", "visakhapatnam")
        weather = await get_weather(loc_id, demo_mode=True)
        warnings = await get_warnings(loc_id, demo_mode=True)
        current_activity = list(state.get("agent_activity", []))
        current_activity.append(AgentEvent(
            agent="Weather Agent",
            action="Loaded simulated severe cyclonic squall telemetry",
            status="completed",
            details="DEMO SIMULATION: Wind 18.5 m/s (36 kts), Rain 48.5mm, Active Red Alert [DEMO / SIMULATED]",
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))
        return {
            "weather": weather,
            "warnings": warnings,
            "agent_activity": current_activity
        }

    weather_res = await WeatherAgent.execute(
        state["target_lat"],
        state["target_lon"],
        state["loc_name"]
    )
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(weather_res["event"])
    return {
        "weather": weather_res["weather"],
        "warnings": weather_res["warnings"],
        "agent_activity": current_activity
    }

async def ocean_node(state: AgentState) -> Dict[str, Any]:
    if state.get("demo_mode"):
        from datetime import datetime
        from ..api.ocean import get_ocean_conditions
        loc_id = state.get("location_id", "visakhapatnam")
        ocean = await get_ocean_conditions(loc_id, demo_mode=True)
        current_activity = list(state.get("agent_activity", []))
        current_activity.append(AgentEvent(
            agent="Ocean Agent",
            action="Loaded simulated extreme sea state conditions",
            status="completed",
            details="DEMO SIMULATION: Waves 4.2m, Swell 3.5m, Current 2.2 m/s [DEMO / SIMULATED]",
            timestamp=datetime.now().strftime("%H:%M:%S")
        ))
        return {
            "ocean": ocean,
            "agent_activity": current_activity
        }

    ocean_res = await OceanAgent.execute(
        state["target_lat"],
        state["target_lon"],
        state["loc_name"]
    )
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(ocean_res["event"])
    return {
        "ocean": ocean_res["ocean"],
        "agent_activity": current_activity
    }

async def pfz_node(state: AgentState) -> Dict[str, Any]:
    pfz_res = await PFZAgent.execute(
        state["target_lat"],
        state["target_lon"],
        state["loc_name"]
    )
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(pfz_res["event"])
    return {
        "pfz": pfz_res["pfz"],
        "agent_activity": current_activity
    }

def gis_node(state: AgentState) -> Dict[str, Any]:
    gis_res = GISAgent.execute(
        state["target_lat"],
        state["target_lon"],
        state["loc_name"]
    )
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(gis_res["event"])
    return {
        "gis_alerts": gis_res["gis_alerts"],
        "agent_activity": current_activity
    }

def risk_node(state: AgentState) -> Dict[str, Any]:
    risk_res = RiskAgent.execute(
        state["weather"],
        state["ocean"],
        state.get("warnings", []),
        state["user_type"]
    )
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(risk_res["event"])
    return {
        "risk": risk_res["risk"],
        "agent_activity": current_activity
    }

async def explanation_node(state: AgentState) -> Dict[str, Any]:
    exp_res = await ExplanationAgent.generate_explanation(
        user_message=state["message"],
        user_type=state["user_type"],
        language=state.get("language", "English"),
        location_name=state["loc_name"],
        risk=state["risk"],
        weather=state["weather"],
        ocean=state["ocean"],
        pfz=state["pfz"],
        warnings=state.get("warnings", []),
        gis_alerts=state.get("gis_alerts", []),
        conversation_history=state.get("history", [])
    )
    current_activity = list(state.get("agent_activity", []))
    current_activity.append(exp_res["event"])
    return {
        "answer": exp_res["answer"],
        "agent_activity": current_activity
    }

# --- Build and Compile LangGraph Workflow ---

def create_orca_graph() -> Any:
    workflow = StateGraph(AgentState)
    
    workflow.add_node("planner", planner_node)
    workflow.add_node("weather_agent", weather_node)
    workflow.add_node("ocean_agent", ocean_node)
    workflow.add_node("pfz_agent", pfz_node)
    workflow.add_node("gis_agent", gis_node)
    workflow.add_node("risk_agent", risk_node)
    workflow.add_node("explanation_agent", explanation_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "weather_agent")
    workflow.add_edge("weather_agent", "ocean_agent")
    workflow.add_edge("ocean_agent", "pfz_agent")
    workflow.add_edge("pfz_agent", "gis_agent")
    workflow.add_edge("gis_agent", "risk_agent")
    workflow.add_edge("risk_agent", "explanation_agent")
    workflow.add_edge("explanation_agent", END)

    return workflow.compile()

# Global compiled LangGraph instance for Member 1 Orchestrator
orca_langgraph = create_orca_graph()

class ORCAGraphOrchestrator:
    """
    Member 1 Lead Orchestrator:
    Manages end-to-end execution of collaborative agents using a compiled LangGraph StateGraph.
    Coordinates Planner -> Data Connectors (Weather, Ocean, PFZ) -> GIS -> Deterministic Risk -> Explanation.
    """

    @staticmethod
    async def run(
        message: str,
        user_type: UserType = "fisherman",
        location_id: str = "visakhapatnam",
        latitude: float = 17.6868,
        longitude: float = 83.2185,
        conversation_id: str = "session_default",
        demo_mode: bool = False
    ) -> ChatResponse:
        
        history = get_conversation_history(conversation_id, limit=6)
        
        initial_state: AgentState = {
            "message": message,
            "user_type": user_type,
            "location_id": location_id,
            "target_lat": latitude,
            "target_lon": longitude,
            "conversation_id": conversation_id,
            "history": history,
            "demo_mode": demo_mode,
            "agent_activity": []
        }

        # Execute through compiled LangGraph
        final_state = await orca_langgraph.ainvoke(initial_state)

        ocean = final_state["ocean"]
        pfz = final_state["pfz"]
        weather = final_state["weather"]

        sources = [
            {"name": "INCOIS Ocean State Forecast", "type": "Oceanographic Telemetry", "status": ocean.data_quality, "timestamp": ocean.timestamp},
            {"name": "INCOIS Marine Fisheries Advisory", "type": "PFZ Advisory", "status": pfz.data_quality, "timestamp": pfz.advisory_date},
            {"name": "IMD Coastal Bulletin", "type": "Meteorological Warning", "status": weather.data_quality, "timestamp": weather.timestamp},
            {"name": "Open-Meteo Global Marine", "type": "Wave & Atmospheric API", "status": "LIVE", "timestamp": "Real-time"}
        ]

        response = ChatResponse(
            conversation_id=conversation_id,
            answer=final_state["answer"],
            language_detected=final_state.get("language", "English"),
            risk=final_state["risk"],
            weather=weather,
            ocean=ocean,
            pfz=pfz,
            warnings=final_state.get("warnings", []),
            gis_alerts=final_state.get("gis_alerts", []),
            sources=sources,
            agent_activity=final_state["agent_activity"]
        )

        loc_info = final_state.get("location_info")
        loc_id_to_save = loc_info.id if loc_info else location_id
        save_chat_turn(conversation_id, user_type, loc_id_to_save, message, response.model_dump())

        return response
