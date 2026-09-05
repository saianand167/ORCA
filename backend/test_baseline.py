import asyncio
import sqlite3
import sys
from pathlib import Path
import httpx

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

async def run_baseline_check():
    print("==================================================")
    print("   ORCA MEMBER 2: STEP 1 - BASELINE VERIFICATION  ")
    print("==================================================")
    print(f"Python Version: {sys.version.split()[0]}")
    
    # 1. Test Open-Meteo Weather API
    print("\n[1/4] Testing Live Weather API (Open-Meteo Forecast)...")
    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=17.6868&longitude=83.2185"
        "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,visibility"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(weather_url)
            if resp.status_code == 200:
                current = resp.json().get("current", {})
                temp = current.get("temperature_2m")
                wind = current.get("wind_speed_10m")
                print(f"   [SUCCESS] Live Weather API Connected!")
                print(f"   Current Telemetry: Temp={temp}°C, Wind Speed={wind} km/h, Time={current.get('time')}")
            else:
                print(f"   [WARNING] Live Weather API returned status code {resp.status_code}")
    except Exception as e:
        print(f"   [ERROR] Failed to connect to Weather API: {e}")

    # 2. Test Open-Meteo Marine API
    print("\n[2/4] Testing Live Marine API (ECMWF/Copernicus Marine)...")
    marine_url = (
        "https://marine-api.open-meteo.com/v1/marine"
        "?latitude=17.6868&longitude=83.2185"
        "&current=wave_height,wave_direction,wave_period,swell_wave_height,ocean_current_velocity,sea_surface_temperature"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(marine_url)
            if resp.status_code == 200:
                current = resp.json().get("current", {})
                wave_h = current.get("wave_height")
                sst = current.get("sea_surface_temperature")
                curr_vel = current.get("ocean_current_velocity")
                print(f"   [SUCCESS] Live Marine API Connected!")
                print(f"   Current Telemetry: Wave Height={wave_h}m, SST={sst}°C, Surface Current={curr_vel} m/s")
            else:
                print(f"   [WARNING] Live Marine API returned status code {resp.status_code}")
    except Exception as e:
        print(f"   [ERROR] Failed to connect to Marine API: {e}")

    # 3. Test SQLite Database
    print("\n[3/4] Testing SQLite Database Initialization...")
    db_path = backend_dir / "app" / "orca.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        print(f"   [SUCCESS] SQLite Connected at: {db_path.name}")
        print(f"   Existing tables: {', '.join(tables) if tables else 'None yet (will auto-create on startup)'}")
    except Exception as e:
        print(f"   [ERROR] SQLite error: {e}")

    # 4. Test Deterministic Risk Engine import
    print("\n[4/4] Testing Risk Engine & Math Logic Import...")
    try:
        from app.core.risk_engine import evaluate_marine_risk
        from app.core.location import haversine_distance_km, calculate_bearing_deg
        
        dist = haversine_distance_km(17.6868, 83.2185, 17.5812, 83.4560)
        bearing = calculate_bearing_deg(17.6868, 83.2185, 17.5812, 83.4560)
        print(f"   [SUCCESS] GIS Functions: Sample distance = {dist} km, Bearing = {bearing}°")
        
        risk = evaluate_marine_risk(weather=None, ocean=None)
        print(f"   [SUCCESS] Risk Engine: Default baseline score = {risk.score}/100, Level = {risk.risk_level}")
    except Exception as e:
        print(f"   [ERROR] Import error: {e}")

    print("\n==================================================")
    print("           BASELINE VERIFICATION COMPLETED        ")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_baseline_check())
