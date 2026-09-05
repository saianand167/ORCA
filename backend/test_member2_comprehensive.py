import asyncio
import sys
import unittest
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.connectors.weather import WeatherProvider
from app.connectors.incois import OceanDataProvider
from app.connectors.pfz import PFZProvider
from app.connectors.imd import IMDProvider
from app.core.location import (
    haversine_distance_km,
    calculate_bearing_deg,
    bearing_to_cardinal,
    is_point_in_polygon
)
from app.core.risk_engine import evaluate_marine_risk, evaluate_risk_from_values
from app.core.models import WeatherData, OceanData, MarineWarning, RiskFactors
from app.database.database import get_cached_data, set_cached_data, get_any_cached_data
from app.main import app

class Member2ComprehensiveTests(unittest.IsolatedAsyncioTestCase):

    async def test_01_live_weather_ingestion(self):
        """Test Live Weather API ingestion, parsing, and normalization."""
        weather = await WeatherProvider.get_weather(17.6868, 83.2185, "Visakhapatnam")
        self.assertIsNotNone(weather)
        self.assertIn(weather.data_quality, ["LIVE", "CACHED"])
        self.assertIsNotNone(weather.wind_speed_ms)
        self.assertIsNotNone(weather.wind_direction_cardinal)
        print(f"\n[PASS] Test 1: Weather Ingested: Temp={weather.temperature_c}C, Wind={weather.wind_speed_ms}m/s ({weather.wind_direction_cardinal}), Quality={weather.data_quality}")

    async def test_02_live_ocean_ingestion_and_provenance(self):
        """Test Live Ocean API ingestion, wave/current parsing, and derived provenance."""
        ocean = await OceanDataProvider.get_ocean_conditions(17.6868, 83.2185, "Visakhapatnam Offshore")
        self.assertIsNotNone(ocean)
        self.assertIn(ocean.data_quality, ["LIVE", "CACHED"])
        self.assertGreater(ocean.significant_wave_height_m, 0.0)
        self.assertGreater(ocean.sea_surface_temperature_c, 15.0)
        # Verify derived metrics and transparent provenance
        self.assertIsNotNone(ocean.chlorophyll_mg_m3)
        self.assertIn("DERIVED", ocean.chlorophyll_provenance)
        self.assertIsNotNone(ocean.mixed_layer_depth_m)
        self.assertIn("DERIVED", ocean.mld_provenance)
        print(f"[PASS] Test 2: Ocean Ingested: Wave={ocean.significant_wave_height_m}m, SST={ocean.sea_surface_temperature_c}C, Chlorophyll={ocean.chlorophyll_mg_m3}mg/m3 ({ocean.chlorophyll_provenance})")

    async def test_03_gis_spatial_calculations(self):
        """Test Great-Circle distance, bearing azimuth, and point-in-polygon geofencing."""
        # Haversine distance check between Visakhapatnam (17.6868, 83.2185) and PFZ Sector 1 (17.5812, 83.4560)
        dist = haversine_distance_km(17.6868, 83.2185, 17.5812, 83.4560)
        self.assertAlmostEqual(dist, 27.77, delta=1.5)

        # Azimuth bearing check
        bearing = calculate_bearing_deg(17.6868, 83.2185, 17.5812, 83.4560)
        cardinal = bearing_to_cardinal(bearing)
        self.assertEqual(cardinal, "ESE")

        # Ray-Casting Point-in-Polygon check
        polygon = [
            [83.0, 17.0],
            [84.0, 17.0],
            [84.0, 18.0],
            [83.0, 18.0],
            [83.0, 17.0]
        ]
        # Point inside
        self.assertTrue(is_point_in_polygon(17.5, 83.5, polygon))
        # Point outside
        self.assertFalse(is_point_in_polygon(19.0, 85.0, polygon))
        print(f"[PASS] Test 3: GIS Math Verified: Dist={dist}km, Bearing={bearing} deg ({cardinal}), Point-in-Polygon=PASSED")

    async def test_04_deterministic_risk_engine_brackets(self):
        """Test Deterministic Risk Engine across all risk levels and weights."""
        # 1. Calm conditions -> LOW RISK (0 - 30)
        calm_w = WeatherData(location="Calm", wind_speed_ms=3.0, data_quality="LIVE")
        calm_o = OceanData(location="Calm", significant_wave_height_m=0.8, surface_current_speed_ms=0.2, data_quality="LIVE")
        risk_calm = evaluate_marine_risk(calm_w, calm_o, warnings=[], user_type="fisherman")
        self.assertEqual(risk_calm.risk_level, "LOW")
        self.assertLessEqual(risk_calm.score, 30)
        self.assertTrue(risk_calm.safe_for_operations)
        self.assertIsNotNone(risk_calm.factor_breakdown)

        # 2. Moderate conditions -> MODERATE RISK (31 - 60)
        mod_w = WeatherData(location="Moderate", wind_speed_ms=7.5, data_quality="LIVE")
        mod_o = OceanData(location="Moderate", significant_wave_height_m=1.7, surface_current_speed_ms=0.5, data_quality="LIVE")
        risk_mod = evaluate_marine_risk(mod_w, mod_o, warnings=[], user_type="fisherman")
        self.assertEqual(risk_mod.risk_level, "MODERATE")
        self.assertTrue(31 <= risk_mod.score <= 60)

        # 3. High conditions with Rough Sea Advisory -> HIGH RISK (61 - 80)
        high_w = WeatherData(location="Rough", wind_speed_ms=11.5, data_quality="LIVE")
        high_o = OceanData(location="Rough", significant_wave_height_m=2.8, surface_current_speed_ms=0.9, data_quality="LIVE")
        high_warn = MarineWarning(
            id="WARN-HIGH-01",
            category="Fishermen Squall Advisory",
            severity="HIGH",
            headline="Squally winds with rough seas over coastal tract",
            description="Small craft advisories in effect; avoid operations beyond 10nm.",
            source="IMD Cyclone Warning Centre"
        )
        risk_high = evaluate_marine_risk(high_w, high_o, warnings=[high_warn], user_type="fisherman")
        self.assertEqual(risk_high.risk_level, "HIGH")
        self.assertTrue(61 <= risk_high.score <= 80)
        self.assertFalse(risk_high.safe_for_operations)

        # 4. Severe conditions with Cyclone Warning -> VERY HIGH RISK (81 - 100)
        severe_w = WeatherData(location="Severe", wind_speed_ms=16.0, data_quality="LIVE")
        severe_o = OceanData(location="Severe", significant_wave_height_m=4.2, surface_current_speed_ms=1.5, data_quality="LIVE")
        cyclone_warn = MarineWarning(
            id="WARN-CYC-01",
            category="Severe Cyclone Warning",
            severity="VERY HIGH",
            headline="Extremely severe cyclonic storm approaching coast",
            description="All fishing activity completely suspended.",
            source="IMD Cyclone Warning Centre"
        )
        risk_severe = evaluate_marine_risk(severe_w, severe_o, warnings=[cyclone_warn], user_type="fisherman")
        self.assertEqual(risk_severe.risk_level, "VERY HIGH")
        self.assertGreaterEqual(risk_severe.score, 81)
        self.assertFalse(risk_severe.safe_for_operations)

        print(f"[PASS] Test 4: Risk Brackets Verified: Calm={risk_calm.score} (LOW), Mod={risk_mod.score} (MODERATE), High={risk_high.score} (HIGH), Severe={risk_severe.score} (VERY HIGH)")

    async def test_05_caching_and_resilient_fallbacks(self):
        """Test SQLite caching read/write and resilient fallback logic."""
        test_key = "test_ocean_99.99_99.99"
        dummy_data = {
            "location": "Test Port",
            "significant_wave_height_m": 1.5,
            "sea_surface_temperature_c": 28.5,
            "data_quality": "LIVE"
        }
        # Write to cache
        set_cached_data(test_key, dummy_data, quality="LIVE")

        # Read fresh cache
        cached = get_cached_data(test_key, max_age_seconds=60)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.get("location"), "Test Port")

        # Test any cached data with age
        cached_tuple = get_any_cached_data(test_key)
        self.assertIsNotNone(cached_tuple)
        cached_obj, age = cached_tuple
        self.assertEqual(cached_obj.get("location"), "Test Port")
        self.assertGreaterEqual(age, 0)
        print(f"[PASS] Test 5: SQLite Caching & Stale-Recovery Verified: Cached Age = {age}s")

    async def test_06_direct_risk_simulation_api(self):
        """Test Direct Simulation API function evaluate_risk_from_values."""
        result = evaluate_risk_from_values(
            wave_height_m=2.1,
            wind_speed_ms=8.0,
            current_speed_ms=0.4,
            warning_severity="MODERATE",
            user_type="fisherman"
        )
        self.assertIsNotNone(result)
        self.assertIn(result.risk_level, ["MODERATE", "HIGH"])
        self.assertIsNotNone(result.factor_breakdown)
        print(f"[PASS] Test 6: Risk Simulation Function: Score={result.score}/100, Level={result.risk_level}, Factors Wave={result.factor_breakdown.wave_score}")

    async def test_07_pfz_advisory_processing(self):
        """Test PFZ advisory dynamic bearing & distance calculation from user location."""
        pfz_res = await PFZProvider.get_pfz_data(17.6868, 83.2185, "Visakhapatnam")
        self.assertTrue(pfz_res.available)
        self.assertGreater(len(pfz_res.locations), 0)
        nearest = pfz_res.nearest_pfz
        self.assertIsNotNone(nearest)
        self.assertGreater(nearest.distance_km, 0.0)
        self.assertIsNotNone(nearest.direction_bearing_deg)
        print(f"[PASS] Test 7: PFZ Advisory: Nearest={nearest.id} at {nearest.distance_km}km ({nearest.sector}), Depth={nearest.depth_m}m")

    def test_08_api_weather_endpoint(self):
        """Test GET /api/weather with both location string and lat/lon params."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test by location ID
        resp1 = client.get("/api/weather?location=visakhapatnam")
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertIn("temperature_c", data1)
        self.assertIn("wind_speed_ms", data1)
        
        # Test by custom lat/lon
        resp2 = client.get("/api/weather?lat=17.6868&lon=83.2185")
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertIn("temperature_c", data2)
        print(f"[PASS] Test 8: GET /api/weather Endpoint Verified (Status 200)")

    def test_09_api_ocean_endpoint(self):
        """Test GET /api/ocean with both location string and lat/lon params."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test by location ID
        resp1 = client.get("/api/ocean?location=visakhapatnam")
        self.assertEqual(resp1.status_code, 200)
        data1 = resp1.json()
        self.assertIn("significant_wave_height_m", data1)
        self.assertIn("chlorophyll_provenance", data1)
        
        # Test by custom lat/lon
        resp2 = client.get("/api/ocean?lat=17.6868&lon=83.2185")
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        self.assertIn("sea_surface_temperature_c", data2)
        print(f"[PASS] Test 9: GET /api/ocean Endpoint Verified (Status 200, Provenance Included)")

    def test_10_api_risk_endpoints(self):
        """Test GET /api/risk and POST /api/risk/evaluate."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # 1. GET /api/risk
        resp_get = client.get("/api/risk?location=visakhapatnam&user_type=fisherman")
        self.assertEqual(resp_get.status_code, 200)
        risk_data = resp_get.json()
        self.assertIn("score", risk_data)
        self.assertIn("risk_level", risk_data)
        self.assertIn("factor_breakdown", risk_data)

        # 2. POST /api/risk/evaluate (simulation)
        payload = {
            "wave_height_m": 2.5,
            "wind_speed_ms": 10.0,
            "current_speed_ms": 0.8,
            "warning_severity": "HIGH",
            "user_type": "fisherman"
        }
        resp_post = client.post("/api/risk/evaluate", json=payload)
        self.assertEqual(resp_post.status_code, 200)
        sim_data = resp_post.json()
        self.assertIn("score", sim_data)
        self.assertIn(sim_data["risk_level"], ["HIGH", "VERY HIGH"])
        print(f"[PASS] Test 10: Risk Endpoints Verified (GET Live Score={risk_data['score']}, POST Simulation Score={sim_data['score']})")

    def test_11_api_map_data_and_sources(self):
        """Test GET /api/map-data and GET /api/sources."""
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Map data
        resp_map = client.get("/api/map-data?location=visakhapatnam")
        self.assertEqual(resp_map.status_code, 200)
        map_json = resp_map.json()
        self.assertIn("pfz_layer", map_json)
        self.assertIn("zones_layer", map_json)
        self.assertIn("risk_zones", map_json)

        # Sources health
        resp_sources = client.get("/api/sources")
        self.assertEqual(resp_sources.status_code, 200)
        sources_list = resp_sources.json()
        self.assertGreater(len(sources_list), 0)
        print(f"[PASS] Test 11: GET /api/map-data & GET /api/sources Verified (Status 200)")

if __name__ == "__main__":
    unittest.main(verbosity=2)
