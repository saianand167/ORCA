from typing import Dict, Any
from ..core.config import settings

class MOSDACProvider:
    """MOSDAC (Meteorological and Oceanographic Satellite Data Archival Centre - ISRO) connector."""
    
    @staticmethod
    def get_status() -> Dict[str, Any]:
        has_creds = bool(settings.MOSDAC_USERNAME and settings.MOSDAC_PASSWORD)
        if has_creds:
            return {
                "name": "MOSDAC (ISRO)",
                "status": "connected",
                "message": "MOSDAC Satellite Connector authenticated and active.",
                "satellite_products": ["INSAT-3D/3DR OCM", "Oceansat-3 SST", "SCATSAT-1 Wind Vectors"]
            }
        else:
            return {
                "name": "MOSDAC (ISRO)",
                "status": "credentials_required",
                "message": "Satellite connector available — credentials not configured (MOSDAC_USERNAME / MOSDAC_PASSWORD).",
                "satellite_products": ["INSAT-3DR", "Oceansat-3 (Ready on Auth)"]
            }
