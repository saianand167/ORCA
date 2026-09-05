"""
ORCA End-to-End Integration & Multi-Agent Test Suite
Verifies end-to-end connectivity across:
- Member 1: AI Multi-Agent Architecture (Planner, Data Agents, GIS, Risk, Explanation, Orchestrator)
- Member 2: Live Data Connectors (Open-Meteo, Marine, Tide, IMD Alerts, Deterministic Risk Engine)
- Member 3: Frontend API payloads, Agent Activity progress events, GIS Map layers
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "ORCA-Integration-Test"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.getcode(), json.loads(res.read().decode("utf-8"))

def post(endpoint: str, data: dict):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "ORCA-Integration-Test"}
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.getcode(), json.loads(res.read().decode("utf-8"))

def run_all_checks():
    passed = 0
    failed = 0

    print("================================================================================")
    print("      ORCA END-TO-END MULTI-AGENT & SERVICES INTEGRATION TEST SUITE            ")
    print("================================================================================")

    # TEST 1: Health Check
    try:
        status, data = get("/api/health")
        assert status == 200 and data.get("status") == "healthy"
        print("[PASS] 1. Backend Core & Health Check (HTTP 200)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 1. Backend Health: {e}")
        failed += 1

    # TEST 2: Member 2 Live Weather Pipeline
    try:
        status, data = get("/api/weather?location=visakhapatnam")
        assert status == 200
        assert data.get("data_quality") in ["LIVE", "CACHED"]
        assert data.get("temperature_c") is not None
        assert data.get("wind_speed_ms") is not None
        assert len(data.get("forecast_hourly", [])) > 0
        print(f"[PASS] 2. Member 2 Live Weather API: {data['temperature_c']}C, Wind {data['wind_speed_ms']} m/s ({data['data_quality']})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. Live Weather API: {e}")
        failed += 1

    # TEST 3: Member 2 Live Ocean Pipeline
    try:
        status, data = get("/api/ocean?location=visakhapatnam")
        assert status == 200
        assert data.get("significant_wave_height_m") is not None
        assert data.get("sea_surface_temperature_c") is not None
        assert data.get("chlorophyll_mg_m3") is not None
        print(f"[PASS] 3. Member 2 Live Ocean State: Waves {data['significant_wave_height_m']}m, SST {data['sea_surface_temperature_c']}C, Current {data['surface_current_speed_ms']}m/s")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 3. Live Ocean State API: {e}")
        failed += 1

    # TEST 4: Member 2 Deterministic Risk Engine
    try:
        status, data = post("/api/risk/evaluate", {
            "wave_height_m": 2.8,
            "wind_speed_ms": 14.5,
            "current_speed_ms": 1.1,
            "warning_severity": "WARNING",
            "user_type": "fisherman"
        })
        assert status == 200
        assert data.get("score") >= 50
        assert len(data.get("reasons", [])) >= 2
        assert "factor_breakdown" in data
        print(f"[PASS] 4. Member 2 Risk Engine: Score {data['score']}/100 -> {data['risk_level']} (Reasons: {len(data['reasons'])})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 4. Risk Engine: {e}")
        failed += 1

    # TEST 5: Member 1 & 2 & 3 Full End-to-End Chat Orchestration (Fisherman Persona)
    try:
        status, data = post("/api/chat", {
            "message": "Can I safely sail out from Visakhapatnam to catch tuna today?",
            "user_type": "fisherman",
            "location_id": "visakhapatnam"
        })
        assert status == 200
        assert "answer" in data and len(data["answer"]) > 50
        assert "agent_activity" in data and len(data["agent_activity"]) >= 5
        assert "risk" in data and "weather" in data and "ocean" in data
        agents_run = [event["agent"] for event in data["agent_activity"]]
        print(f"[PASS] 5. Member 1 Orchestrator (Fisherman): Executed agents: {', '.join(agents_run)}")
        print(f"       Risk: {data['risk']['risk_level']} ({data['risk']['score']}/100) | Activity steps: {len(data['agent_activity'])}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 5. Orchestrator Fisherman Chat: {e}")
        failed += 1

    # TEST 6: Member 1 & 2 & 3 Orchestration (Researcher Persona & Southern Coast)
    try:
        status, data = post("/api/chat", {
            "message": "Analyze mixed layer depth and chlorophyll gradients near Kochi for oceanographic survey.",
            "user_type": "ocean_researcher",
            "location_id": "kochi"
        })
        assert status == 200
        assert "answer" in data
        assert data["ocean"]["location"] == "Kochi"
        assert data["ocean"]["mixed_layer_depth_m"] is not None
        print(f"[PASS] 6. Member 1 Orchestrator (Researcher @ Kochi): MLD={data['ocean']['mixed_layer_depth_m']}m, Chl={data['ocean']['chlorophyll_mg_m3']} mg/m3")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 6. Orchestrator Researcher Chat: {e}")
        failed += 1

    # TEST 7: Member 3 Map Data Payload & PFZ Coordinates
    try:
        status, data = get("/api/map-data")
        assert status == 200
        assert "location" in data and "pfz_layer" in data and "zones_layer" in data and "risk_zones" in data
        pfz_count = len(data["pfz_layer"])
        zones_count = len(data["zones_layer"])
        print(f"[PASS] 7. Member 3 GIS Map Data: Location '{data['location']['name']}', {pfz_count} PFZ targets, {zones_count} spatial zones")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 7. GIS Map Data API: {e}")
        failed += 1

    # TEST 8: Member 3 Potential Fishing Zones (PFZ) Feed
    try:
        status, data = get("/api/pfz?location=visakhapatnam")
        assert status == 200
        assert data.get("available") is True
        assert len(data.get("locations", [])) > 0
        assert data.get("nearest_pfz") is not None
        nearest = data["nearest_pfz"]
        print(f"[PASS] 8. Member 3 PFZ Advisory: Nearest {nearest['id']} at {nearest['distance_km']}km bearing {nearest['sector']} (Target: {', '.join(nearest['fish_species_likely'][:2])})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 8. PFZ API: {e}")
        failed += 1

    # TEST 9: Member 3 Marine Warnings & Bulletins
    try:
        status, data = get("/api/warnings?location=visakhapatnam")
        assert status == 200
        assert isinstance(data, list)
        print(f"[PASS] 9. Member 3 Marine Warnings: Retrieved {len(data)} active advisories/bulletins")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 9. Warnings API: {e}")
        failed += 1

    # TEST 10: Member 2 Data Source Telemetry & Audit Registry
    try:
        status, data = get("/api/sources")
        assert status == 200
        assert isinstance(data, list)
        live_count = sum(1 for s in data if s.get("data_quality") == "LIVE")
        print(f"[PASS] 10. Data Source Registry: {len(data)} connectors tracked ({live_count} LIVE pipelines)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 10. Sources API: {e}")
        failed += 1

    print("================================================================================")
    print(f"TEST RESULTS: {passed} PASSED, {failed} FAILED (TOTAL: {passed + failed})")
    print("================================================================================")
    return failed == 0

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
