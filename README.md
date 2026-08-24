# ORCA — Marine Ecosystem Reasoning with Collaborative Agents
### ISRO Smart India Hackathon Prototype (SIH26176)

ORCA is an Agentic AI-powered Marine Intelligence Platform developed for the Indian Space Research Organisation (ISRO) and Indian coastal stakeholders. It autonomously interprets conversational marine queries, decomposes requests into specialized agent tasks, correlates real-time oceanographic and meteorological telemetry, calculates deterministic marine operational safety risks, and provides explainable decision support.

---

## 🌊 System Architecture

```
                                USER QUERY
                                    │
                                    ▼
                          CONVERSATIONAL UI
                      (React + Vite + Tailwind)
                                    │
                                    ▼
                           PLANNER AGENT
                                    │
       ┌──────────────┬─────────────┼─────────────┬──────────────┐
       ▼              ▼             ▼             ▼              ▼
  Weather Agent  Ocean Agent    PFZ Agent     GIS Agent     Tide / Satellite
  (IMD / Meteo) (INCOIS OSF)  (INCOIS PFZ)  (MPAs & IMBL)   (MOSDAC ISRO)
       │              │             │             │              │
       └──────────────┴─────────────┼─────────────┴──────────────┘
                                    ▼
                         DATA NORMALIZATION & CACHE
                               (SQLite)
                                    │
                                    ▼
                       DETERMINISTIC RISK ENGINE
                     (0-100 Multi-Parameter Model)
                                    │
                                    ▼
                         EXPLANATION AGENT
                     (Groq Llama-3.3 / Deterministic)
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
         CONVERSATIONAL ANSWER                 MAP LAYERS
   (Evidence + Risk + Citations)     (PFZ + Risk Polygons + MPAs)
```

---

## 👥 Target User Roles

1. **🎣 Fisherman**:
   - Safety checks: *"Can I go fishing tomorrow morning near Vizag?"*
   - Nearest Potential Fishing Zones (PFZ) with bearing, distance in km/nautical miles, depth contour, and species.
   - Coastal squall and weather warnings from IMD Cyclone Warning Centre.
2. **🔬 Ocean Researcher**:
   - Sea Surface Temperature (SST) & chlorophyll-a concentrations.
   - Surface current vectors, swell spectra, and Mixed Layer Depth (MLD).
   - Thermal front and oceanic eddy boundary analysis.
3. **🚢 Ship / Marine Operator**:
   - Lower-risk maritime route corridors and sea state risk indices.
   - Gale wind alerts, high wave warnings, and port anchorage condition.

---

## 📡 Data Connectors & Integrations

- **INCOIS Ocean State Forecast (OSF)**: Significant wave height, wave period, swell height/period, surface current speed & direction, SST, MLD, and chlorophyll.
- **INCOIS Potential Fishing Zones (PFZ)**: Spatial satellite advisory with dynamic distance and compass bearing from any user coordinates.
- **India Meteorological Department (IMD)**: Coastal weather bulletins, squall warnings, fishermen advisories, and cyclone tracking.
- **Open-Meteo Global Marine & Atmospheric API**: Live real-time wave and meteorological telemetry feed.
- **MOSDAC (ISRO)**: Satellite Earth Observation abstraction connector with credential-aware status reporting.
- **Deterministic Risk Engine**: Configurable thresholds (`backend/app/config/risk_thresholds.yaml`) producing transparent safety ratings (LOW, MODERATE, HIGH, VERY HIGH) without arbitrary LLM hallucinations.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Backend Setup

```bash
cd orca/backend

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Set your Groq API key in .env for Llama-3.3 reasoning
# GROQ_API_KEY=your_key_here

# Start FastAPI backend server
uvicorn app.main:app --reload --port 8000
```
Backend runs at: `http://localhost:8000`  
API Docs (Swagger): `http://localhost:8000/docs`

### 2. Frontend Setup

```bash
cd orca/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend runs at: `http://localhost:5173`

---

## 🛡️ Responsible AI & Disclaimer

> [!IMPORTANT]
> ORCA is a prototype decision-support system developed for educational and hackathon demonstration purposes. Marine conditions can change rapidly. Users must always verify official marine, coastal, and navigation advisories from INCOIS, IMD, and the Indian Coast Guard prior to undertaking any voyage.
