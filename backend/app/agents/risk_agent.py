from datetime import datetime
from typing import Dict, Any, List
from ..core.models import AgentEvent, WeatherData, OceanData, MarineWarning, UserType
from ..core.risk_engine import evaluate_marine_risk

class RiskAgent:
    """Risk Agent: Evaluates multi-parameter deterministic marine risk."""
    
    @staticmethod
    def execute(
        weather: WeatherData,
        ocean: OceanData,
        warnings: List[MarineWarning],
        user_type: UserType
    ) -> Dict[str, Any]:
        risk_result = evaluate_marine_risk(weather, ocean, warnings, user_type)
        
        event = AgentEvent(
            agent="Risk Agent",
            action=f"Computed deterministic safety score ({risk_result.score}/100)",
            status="completed",
            details=f"Risk Level: {risk_result.risk_level} ({risk_result.score}/100). Key factors: {', '.join(risk_result.reasons[:2])}",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )
        
        return {
            "risk": risk_result,
            "event": event
        }
