import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..core.models import AgentEvent, WeatherData, OceanData, PFZData, MarineWarning, RiskAssessment, UserType
from ..core.config import settings

class ExplanationAgent:
    """Explanation Agent: Generates clear, explainable, evidence-grounded marine advisory using Groq LLM or deterministic engine."""
    
    @staticmethod
    async def generate_explanation(
        user_message: str,
        user_type: UserType,
        language: str,
        location_name: str,
        risk: RiskAssessment,
        weather: WeatherData,
        ocean: OceanData,
        pfz: PFZData,
        warnings: List[MarineWarning],
        gis_alerts: List[Dict[str, Any]],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        # Build strict fact payload
        facts = {
            "location": location_name,
            "user_role": user_type,
            "risk_assessment": {
                "level": risk.risk_level,
                "score": f"{risk.score}/100",
                "reasons": risk.reasons,
                "safe_for_operations": risk.safe_for_operations
            },
            "atmospheric_weather": {
                "condition": weather.condition,
                "temperature": f"{weather.temperature_c}°C",
                "wind_speed": f"{weather.wind_speed_ms} m/s ({weather.wind_speed_knots} knots)",
                "wind_direction": f"{weather.wind_direction_cardinal} ({weather.wind_direction_deg}°)",
                "source": weather.source,
                "quality": weather.data_quality
            },
            "ocean_state": {
                "wave_height": f"{ocean.significant_wave_height_m} m",
                "wave_period": f"{ocean.wave_period_s} s",
                "swell_height": f"{ocean.swell_height_m} m",
                "surface_current": f"{ocean.surface_current_speed_ms} m/s",
                "sea_surface_temp": f"{ocean.sea_surface_temperature_c}°C",
                "chlorophyll": f"{ocean.chlorophyll_mg_m3} mg/m³",
                "source": ocean.source,
                "quality": ocean.data_quality
            },
            "potential_fishing_zones": {
                "available": pfz.available,
                "count": len(pfz.locations),
                "nearest": {
                    "id": pfz.nearest_pfz.id if pfz.nearest_pfz else None,
                    "distance": f"{pfz.nearest_pfz.distance_km} km ({pfz.nearest_pfz.distance_nm} nm)" if pfz.nearest_pfz else None,
                    "sector": pfz.nearest_pfz.sector if pfz.nearest_pfz else None,
                    "depth": pfz.nearest_pfz.depth_m if pfz.nearest_pfz else None,
                    "species": pfz.nearest_pfz.fish_species_likely if pfz.nearest_pfz else []
                } if pfz.nearest_pfz else None,
                "valid_until": pfz.valid_until
            },
            "marine_warnings": [
                {"headline": w.headline, "severity": w.severity, "source": w.source} for w in warnings
            ],
            "geofence_alerts": gis_alerts
        }

        explanation_text = ""
        llm_used = "Groq Llama-3.3"

        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY)
                
                system_prompt = f"""You are ORCA (Marine Ecosystem Reasoning with Collaborative Agents), an AI marine intelligence assistant developed for ISRO & Indian coastal stakeholders.
Role context: Assisting a '{user_type}'.
Language: Respond in {language} (if regional language like Telugu/Hindi/Tamil is requested, provide clear guidance, otherwise English).

CRITICAL CONSTRAINTS:
1. ONLY reference the verified telemetry facts provided in JSON. NEVER fabricate weather, wave, or PFZ data.
2. If data is missing or marked N/A, clearly say 'Data unavailable'.
3. Always provide clear, structured bullet points covering:
   - Marine Risk Rating & Operational Advice
   - Prevailing Wind & Wave Conditions
   - Potential Fishing Zones / Ocean Parameters relevant to the user
   - Official Marine Warnings & Spatial Boundaries
4. Always conclude with the mandatory disclaimer: 'Note: ORCA provides prototype decision-support based on available data. Always verify official INCOIS and IMD marine advisories before venturing out.'
"""
                chat_messages = [
                    {"role": "system", "content": system_prompt}
                ]
                
                # Add up to 3 recent conversational turns
                for h in conversation_history[-3:]:
                    chat_messages.append({"role": "user" if h["sender"] == "user" else "assistant", "content": h["message"]})
                    
                chat_messages.append({
                    "role": "user",
                    "content": f"User question: '{user_message}'\n\nVerified Ground Truth Telemetry Facts:\n{json.dumps(facts, indent=2)}"
                })

                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=chat_messages,
                    temperature=0.2,
                    max_tokens=650
                )
                explanation_text = completion.choices[0].message.content
            except Exception as e:
                # Fallback on LLM failure
                explanation_text = ExplanationAgent._generate_deterministic_explanation(
                    user_message, user_type, location_name, risk, weather, ocean, pfz, warnings, gis_alerts
                )
                llm_used = "Deterministic Reasoning Engine (Fallback)"
        else:
            explanation_text = ExplanationAgent._generate_deterministic_explanation(
                user_message, user_type, location_name, risk, weather, ocean, pfz, warnings, gis_alerts
            )
            llm_used = "Deterministic Reasoning Engine"

        event = AgentEvent(
            agent="Explanation Agent",
            action=f"Synthesized evidence-based marine advisory via {llm_used}",
            status="completed",
            details=f"Generated structured explanation with {len(risk.reasons)} risk factors and telemetry citations.",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )

        return {
            "answer": explanation_text,
            "facts": facts,
            "event": event
        }

    @staticmethod
    def _generate_deterministic_explanation(
        user_message: str,
        user_type: UserType,
        location_name: str,
        risk: RiskAssessment,
        weather: WeatherData,
        ocean: OceanData,
        pfz: PFZData,
        warnings: List[MarineWarning],
        gis_alerts: List[Dict[str, Any]]
    ) -> str:
        status_banner = "✅ Lower-risk operating conditions" if risk.risk_level in ["LOW", "MODERATE"] else "⚠️ Elevated marine risk advisory"
        
        pfz_snippet = ""
        if pfz.available and pfz.nearest_pfz:
            n = pfz.nearest_pfz
            pfz_snippet = f"\n- **Nearest Fishing Zone (PFZ)**: {n.id} located **{n.distance_km} km** ({n.distance_nm} nm) bearing **{n.sector}**, depth **{n.depth_m}m** (Target species: {', '.join(n.fish_species_likely[:3])})."
            
        warning_snippet = ""
        if warnings:
            w_heads = [f"{w.headline} ({w.source})" for w in warnings[:2]]
            warning_snippet = f"\n- **Active Advisories**: {'; '.join(w_heads)}"

        gis_snippet = ""
        if gis_alerts:
            g_heads = [f"{g['name']} ({g['distance_km']} km)" for g in gis_alerts]
            gis_snippet = f"\n- **Geospatial Note**: Proximity to {'; '.join(g_heads)}."

        return f"""### Marine Intelligence Report — {location_name}

**Status**: **{risk.risk_level} RISK** ({risk.score}/100) — *{status_banner}*

#### Key Telemetry & Observations:
- **Sea State & Waves**: Significant wave height of **{ocean.significant_wave_height_m} m** (Period: {ocean.wave_period_s}s, Swell: {ocean.swell_height_m}m).
- **Wind Conditions**: **{weather.wind_speed_ms} m/s** ({weather.wind_speed_knots} kts) from the **{weather.wind_direction_cardinal}** ({weather.condition}).
- **Sea Surface Temperature (SST)**: **{ocean.sea_surface_temperature_c}°C** | Surface Current: **{ocean.surface_current_speed_ms} m/s**.{pfz_snippet}{warning_snippet}{gis_snippet}

#### Operational Recommendation:
{risk.summary} Based on current prototype telemetry, conditions are within operational parameters for motorized vessels, but offshore swells should be monitored.

*Disclaimer: ORCA provides prototype decision-support based on available data. Always verify official INCOIS and IMD marine advisories before venturing out.*"""
