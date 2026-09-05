import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..core.models import AgentEvent, WeatherData, OceanData, PFZData, MarineWarning, RiskAssessment, UserType
from ..core.config import settings
from ..connectors.tide import TideProvider

class ExplanationAgent:
    """
    Explanation Agent (Member 1 Lead):
    Synthesizes evidence-grounded, multi-lingual, and persona-tailored marine intelligence
    advisories using Groq Llama-3.3 LLM (with strict telemetry facts JSON prompt)
    or the deterministic marine reasoning engine.
    """
    
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
        
        # Calculate current astronomical tide stage using harmonic constituent analysis
        tide_info = TideProvider.get_tide_info(location_name)
        
        # Build strict fact payload
        facts = {
            "location": location_name,
            "user_role": user_type,
            "language_requested": language,
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
                "visibility": f"{weather.visibility_km} km",
                "source": weather.source,
                "quality": weather.data_quality
            },
            "ocean_state": {
                "wave_height": f"{ocean.significant_wave_height_m} m",
                "wave_period": f"{ocean.wave_period_s} s",
                "swell_height": f"{ocean.swell_height_m} m",
                "surface_current": f"{ocean.surface_current_speed_ms} m/s ({ocean.surface_current_direction_deg}°)",
                "sea_surface_temp": f"{ocean.sea_surface_temperature_c}°C",
                "chlorophyll": f"{ocean.chlorophyll_mg_m3} mg/m³",
                "mixed_layer_depth": f"{ocean.mixed_layer_depth_m} m",
                "source": ocean.source,
                "quality": ocean.data_quality
            },
            "astronomical_tide": {
                "height_m": f"{tide_info.get('current_height_m', 0.85)} m",
                "phase": tide_info.get('tidal_phase', 'Transitional'),
                "type": tide_info.get('tide_type', 'Semi-diurnal'),
                "model": "Harmonic Astronomical Constituents (M2, S2, K1, O1)"
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
                
                tide_phase_str = tide_info.get('tidal_phase', 'Transitional')
                tide_ht_str = tide_info.get('current_height_m', 0.85)

                system_prompt = f"""You are ORCA (Marine Ecosystem Reasoning with Collaborative Agents), an advanced Agentic AI Marine Intelligence Platform developed for ISRO & Indian coastal stakeholders.
User Operational Role: {user_type} (tailor your operational recommendations for this specific role, e.g. artisanal fishermen, ocean researchers, or ship operators).
Language: Respond naturally in {language} (if Telugu/Hindi/Tamil requested, write the advisory clearly in that language with technical terms).

CORE INSTRUCTIONS:
1. DYNAMIC REASONING: Read the user's specific query carefully and address it directly. Do NOT output a static, rigid template or predefined repetitive bullet blocks unless asked.
2. GROUNDED IN REAL-TIME FACTS: You are provided with real-time verified ground-truth marine telemetry facts (wind speed, wave height, swell, currents, sea surface temperature, tide stage, PFZ coordinates, risk score, official warnings). You MUST cite and explain these real-time values accurately to justify your recommendations.
3. OPERATIONAL ADVICE: Provide clear, practical safety guidance appropriate for the user's vessel/role.
4. SAFETY DISCLAIMER: Conclude with a brief standard safety sentence: 'Always verify official INCOIS and IMD bulletins before sailing.'
"""
                chat_messages = [
                    {"role": "system", "content": system_prompt}
                ]
                
                for h in conversation_history[-3:]:
                    chat_messages.append({"role": "user" if h["sender"] == "user" else "assistant", "content": h["message"]})
                    
                chat_messages.append({
                    "role": "user",
                    "content": f"User question: '{user_message}'\n\nVerified Ground Truth Telemetry Facts for {location_name}:\n{json.dumps(facts, indent=2)}\n\nPlease provide a clear, conversational, and direct answer based on these real-time verified facts:"
                })

                candidate_models = [
                    "qwen/qwen3.8-27b",
                    "openai/gpt-oss-120b",
                    "groq/compound",
                    "groq/compound-mini",
                    "openai/gpt-oss-20b",
                    "llama-3.3-70b-versatile"
                ]
                completion = None
                chosen_model = None
                for candidate in candidate_models:
                    try:
                        completion = client.chat.completions.create(
                            model=candidate,
                            messages=chat_messages,
                            temperature=0.4,
                            max_tokens=650
                        )
                        chosen_model = candidate
                        break
                    except Exception as err:
                        print(f"[ORCA Groq Warning] Model {candidate} failed: {err}")
                        continue

                if completion and completion.choices:
                    explanation_text = completion.choices[0].message.content
                    llm_used = f"Groq ({chosen_model})"
                    print(f"[ORCA Groq Success] Answer generated via Groq ({chosen_model}) for query: '{user_message[:40]}'")
                else:
                    explanation_text = ExplanationAgent._generate_deterministic_explanation(
                        user_message, user_type, location_name, language, risk, weather, ocean, pfz, warnings, gis_alerts, tide_info
                    )
                    llm_used = "Deterministic Reasoning Engine (Fallback)"
            except Exception:
                explanation_text = ExplanationAgent._generate_deterministic_explanation(
                    user_message, user_type, location_name, language, risk, weather, ocean, pfz, warnings, gis_alerts, tide_info
                )
                llm_used = "Deterministic Reasoning Engine (Fallback)"
        else:
            explanation_text = ExplanationAgent._generate_deterministic_explanation(
                user_message, user_type, location_name, language, risk, weather, ocean, pfz, warnings, gis_alerts, tide_info
            )
            llm_used = "Deterministic Reasoning Engine"

        event = AgentEvent(
            agent="Explanation Agent",
            action=f"Synthesized evidence-based marine advisory via {llm_used}",
            status="completed",
            details=f"Generated structured explanation in {language} for role '{user_type}' with {len(risk.reasons)} risk factors and telemetry citations.",
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
        language: str,
        risk: RiskAssessment,
        weather: WeatherData,
        ocean: OceanData,
        pfz: PFZData,
        warnings: List[MarineWarning],
        gis_alerts: List[Dict[str, Any]],
        tide_info: Dict[str, Any]
    ) -> str:
        status_banner = "Lower-risk operating conditions" if risk.risk_level in ["LOW", "MODERATE"] else "Elevated marine risk advisory"
        
        # Multi-lingual header greeting
        greeting = ""
        if language == "Telugu":
            greeting = f"**నమస్కారం! {location_name} సముద్ర సమాచారం:**\n\n"
        elif language == "Hindi":
            greeting = f"**नमस्ते! {location_name} समुद्री मौसम और जोखिम परामर्श:**\n\n"
        elif language == "Tamil":
            greeting = f"**வணக்கம்! {location_name} கடல்சார் தகவல் மற்றும் எச்சரிக்கை:**\n\n"

        # Persona-specific sections
        role_advice = ""
        if user_type == "fisherman":
            pfz_line = "No active PFZ detected in the immediate coastal sector."
            if pfz.available and pfz.nearest_pfz:
                n = pfz.nearest_pfz
                pfz_line = f"Zone **{n.id}** is located **{n.distance_km} km** ({n.distance_nm} nm) bearing **{n.sector}**, depth **{n.depth_m}m**. Likely catch: **{', '.join(n.fish_species_likely[:3])}**."

            craft_safety = "Safe for small motorized boats (<10m) and mechanized trawlers." if risk.safe_for_operations else "Unsafe for traditional non-motorized and small motorized craft. Mechanized vessels should exercise extreme caution."

            tide_ht = tide_info.get('current_height_m', 0.85)
            tide_ph = tide_info.get('tidal_phase', 'Transitional')
            tide_tp = tide_info.get('tide_type', 'Semi-diurnal')

            role_advice = f"""#### Fisherfolk Operational Guidance:
- **Potential Fishing Zone (PFZ)**: {pfz_line}
- **Vessel Safety**: {craft_safety}
- **Tidal Navigation**: Astronomical water level is **{tide_ht}m** ({tide_ph} / {tide_tp}). Optimal harbor departure during flood stages."""

        elif user_type == "ocean_researcher":
            tide_ht = tide_info.get('current_height_m', 0.85)
            tide_ph = tide_info.get('tidal_phase', 'Transitional')
            role_advice = f"""#### Oceanographic Research & Physical Telemetry:
- **Mixed Layer Depth (MLD)**: **{ocean.mixed_layer_depth_m} m** (Derived via Thermocline Boundary Layer Model).
- **Chlorophyll-a Proxy**: **{ocean.chlorophyll_mg_m3} mg/m³** (Surface enrichment from coastal upwelling).
- **Water Column & Currents**: SST **{ocean.sea_surface_temperature_c}°C**, surface drift **{ocean.surface_current_speed_ms} m/s** heading {ocean.surface_current_direction_deg}°.
- **Tide Constituent Analysis**: Astronomical water level **{tide_ht} m** ({tide_ph})."""

        else:  # ship_operator
            tide_ht = tide_info.get('current_height_m', 0.85)
            tide_ph = tide_info.get('tidal_phase', 'Transitional')
            role_advice = f"""#### Port & Vessel Navigation Advisory:
- **Sea State & Fairway**: Significant wave height **{ocean.significant_wave_height_m} m**, wave period **{ocean.wave_period_s} s**, deep swell **{ocean.swell_height_m} m**.
- **Wind Drift & Crosswinds**: **{weather.wind_speed_ms} m/s** ({weather.wind_speed_knots} kts) from **{weather.wind_direction_cardinal}** ({weather.wind_direction_deg}°).
- **Harbor Approach**: Tidal elevation at **{tide_ht} m** ({tide_ph}). Maintain standard safety draft."""

        warning_snippet = ""
        if warnings:
            w_heads = [f"{w.headline} ({w.source})" for w in warnings[:2]]
            warning_snippet = f"\n- **Active Official Advisories**: {'; '.join(w_heads)}"

        gis_snippet = ""
        if gis_alerts:
            g_heads = [f"{g['name']} ({g['distance_km']} km)" for g in gis_alerts]
            gis_snippet = f"\n- **Geospatial Boundary Alerts**: Proximity to {'; '.join(g_heads)}."

        return f"""{greeting}### Marine Intelligence Report — {location_name}

**Status**: **{risk.risk_level} RISK** ({risk.score}/100) — *{status_banner}*

#### Key Live Telemetry & Observations:
- **Sea State & Waves**: Significant wave height of **{ocean.significant_wave_height_m} m** (Period: {ocean.wave_period_s}s, Swell: {ocean.swell_height_m}m).
- **Wind Conditions**: **{weather.wind_speed_ms} m/s** ({weather.wind_speed_knots} kts) from the **{weather.wind_direction_cardinal}** ({weather.condition}).
- **Sea Surface Temperature (SST)**: **{ocean.sea_surface_temperature_c}°C** | Surface Current: **{ocean.surface_current_speed_ms} m/s**.{warning_snippet}{gis_snippet}

{role_advice}

#### Operational Summary:
{risk.summary}

*Disclaimer: ORCA provides prototype decision-support based on available data. Always verify official INCOIS and IMD marine advisories before venturing out.*"""
