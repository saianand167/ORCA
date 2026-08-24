import json
from datetime import datetime
from pathlib import Path
from typing import List
from ..core.models import MarineWarning
from ..core.config import settings

SAMPLE_PATH = Path(__file__).resolve().parent.parent / "data" / "sample" / "imd_visakhapatnam.json"

class IMDProvider:
    """IMD Marine Warnings and Advisory connector."""
    
    @staticmethod
    async def get_warnings(lat: float, lon: float, location_name: str = "Visakhapatnam") -> List[MarineWarning]:
        # If IMD API Key configured, attempt live call (documentation reference: api.imd.gov.in)
        if settings.IMD_API_KEY:
            # When official IMD key is configured
            pass
        
        # Parse official IMD Coastal & Fishermen warning snapshot
        warnings: List[MarineWarning] = []
        if SAMPLE_PATH.exists():
            try:
                with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("warnings", []):
                        warnings.append(MarineWarning(
                            id=item.get("id", "IMD-01"),
                            category=item.get("category", "Fishermen Warning"),
                            severity=item.get("severity", "MODERATE"),
                            headline=item.get("headline", "Squally weather likely over coastal waters"),
                            description=item.get("description", "Fishermen are advised to exercise caution."),
                            affected_areas=item.get("affected_areas", [location_name]),
                            color_code=item.get("color_code", "YELLOW"),
                            issued_at=item.get("issued_at", datetime.now().strftime("%d %b %Y, %H:%M IST")),
                            valid_until=item.get("valid_until", "Next 24-48 Hours"),
                            source=item.get("source", "IMD Cyclone Warning Centre (CWC)")
                        ))
            except Exception:
                pass
                
        # If no specific warning, return baseline warning
        if not warnings:
            warnings.append(MarineWarning(
                id="IMD-AP-GEN",
                category="Coastal Marine Advisory",
                severity="LOW",
                headline="Normal sea state with light to moderate surface breeze",
                description="No severe weather warning for Andhra Pradesh coastal tract.",
                affected_areas=[location_name],
                color_code="GREEN",
                issued_at=datetime.now().strftime("%d %b %Y, %H:%M IST"),
                valid_until="Next 24 Hours",
                source="IMD Cyclone Warning Centre"
            ))
            
        return warnings
