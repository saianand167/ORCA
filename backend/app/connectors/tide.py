from datetime import datetime
from typing import Dict, Any

class TideProvider:
    """Tide data provider abstraction."""
    
    @staticmethod
    def get_tide_info(location_name: str = "Visakhapatnam") -> Dict[str, Any]:
        return {
            "location": location_name,
            "status": "available",
            "source": "INCOIS Coastal Tide Network",
            "high_tides": [
                {"time": "04:15 IST", "height_m": 1.62},
                {"time": "16:40 IST", "height_m": 1.78}
            ],
            "low_tides": [
                {"time": "10:30 IST", "height_m": 0.45},
                {"time": "22:50 IST", "height_m": 0.52}
            ],
            "tidal_phase": "Flood Tide (Rising)",
            "timestamp": datetime.now().strftime("%d %b %Y, %H:%M IST")
        }
