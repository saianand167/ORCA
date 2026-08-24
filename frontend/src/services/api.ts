import {
  LocationInfo,
  WeatherData,
  OceanData,
  PFZData,
  MarineWarning,
  SourceHealth,
  UserRole
} from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  async getLocations(): Promise<LocationInfo[]> {
    try {
      const res = await fetch(`${API_BASE}/location`);
      if (!res.ok) throw new Error('Failed to fetch locations');
      return await res.json();
    } catch {
      return [
        {
          id: 'visakhapatnam',
          name: 'Visakhapatnam',
          state: 'Andhra Pradesh',
          coordinates: { latitude: 17.6868, longitude: 83.2185 },
          coastal_body: 'Bay of Bengal',
          is_primary: true,
          description: "Major port and primary operational marine zone on India's eastern seaboard."
        },
        {
          id: 'kakinada',
          name: 'Kakinada',
          state: 'Andhra Pradesh',
          coordinates: { latitude: 16.9891, longitude: 82.2475 },
          coastal_body: 'Bay of Bengal',
          is_primary: false
        },
        {
          id: 'chennai',
          name: 'Chennai',
          state: 'Tamil Nadu',
          coordinates: { latitude: 13.0827, longitude: 80.2707 },
          coastal_body: 'Bay of Bengal',
          is_primary: false
        },
        {
          id: 'kochi',
          name: 'Kochi',
          state: 'Kerala',
          coordinates: { latitude: 9.9312, longitude: 76.2673 },
          coastal_body: 'Arabian Sea',
          is_primary: false
        },
        {
          id: 'mumbai',
          name: 'Mumbai',
          state: 'Maharashtra',
          coordinates: { latitude: 18.922, longitude: 72.8347 },
          coastal_body: 'Arabian Sea',
          is_primary: false
        }
      ];
    }
  },

  async getWeather(locationId: string): Promise<WeatherData> {
    const res = await fetch(`${API_BASE}/weather?location=${encodeURIComponent(locationId)}`);
    if (!res.ok) throw new Error('Weather API error');
    return await res.json();
  },

  async getOcean(locationId: string): Promise<OceanData> {
    const res = await fetch(`${API_BASE}/ocean?location=${encodeURIComponent(locationId)}`);
    if (!res.ok) throw new Error('Ocean API error');
    return await res.json();
  },

  async getPFZ(locationId: string): Promise<PFZData> {
    const res = await fetch(`${API_BASE}/pfz?location=${encodeURIComponent(locationId)}`);
    if (!res.ok) throw new Error('PFZ API error');
    return await res.json();
  },

  async getWarnings(locationId: string): Promise<MarineWarning[]> {
    const res = await fetch(`${API_BASE}/warnings?location=${encodeURIComponent(locationId)}`);
    if (!res.ok) throw new Error('Warnings API error');
    return await res.json();
  },

  async getMapData(locationId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/map-data?location=${encodeURIComponent(locationId)}`);
    if (!res.ok) throw new Error('Map Data API error');
    return await res.json();
  },

  async getSources(): Promise<SourceHealth[]> {
    const res = await fetch(`${API_BASE}/sources`);
    if (!res.ok) throw new Error('Sources API error');
    return await res.json();
  },

  async getSystemStatus(): Promise<any> {
    const res = await fetch(`${API_BASE}/system-status`);
    if (!res.ok) throw new Error('System status API error');
    return await res.json();
  },

  async sendChatMessage(payload: {
    message: string;
    location_id: string;
    latitude?: number;
    longitude?: number;
    user_type: UserRole;
    conversation_id?: string;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Chat agent API error');
    return await res.json();
  }
};
