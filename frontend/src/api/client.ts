import { SystemHealthData } from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<SystemHealthData> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) {
      throw new Error(`Health check failed: HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    return {
      status: 'unhealthy',
      app_name: 'FIM Enterprise',
      version: '1.0.0',
      environment: 'disconnected',
      timestamp: new Date().toISOString(),
      services: {
        api: { status: 'unhealthy', details: { error: String(err) } },
      },
    };
  }
}
