import { getStoredAuth } from './auth';
import { EndpointItem } from '../types';

const API_BASE = '/api/v1';

function getAuthHeaders(): HeadersInit {
  const { token } = getStoredAuth();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export interface InstallerInfo {
  server_url: string;
  enrollment_token: string;
  windows: {
    powershell_command: string;
    exe_download_url: string;
    msi_download_url: string;
  };
  linux: {
    bash_command: string;
    script_download_url: string;
  };
}

export async function fetchEndpoints(search?: string, status?: string): Promise<{ items: EndpointItem[]; total: number }> {
  try {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status && status !== 'all') params.append('status', status);

    const url = `${API_BASE}/endpoints${params.toString() ? `?${params.toString()}` : ''}`;
    const res = await fetch(url, {
      headers: getAuthHeaders(),
    });

    if (!res.ok) {
      return { items: [], total: 0 };
    }

    const data = await res.json();
    return data;
  } catch {
    return { items: [], total: 0 };
  }
}

export async function fetchInstallerInfo(): Promise<InstallerInfo | null> {
  try {
    const res = await fetch(`${API_BASE}/agents/installer-info`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function revokeEndpoint(endpointId: string): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE}/endpoints/${endpointId}/revoke`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    const data = await res.json();
    return { success: res.ok, message: data.message || 'Revoke operation completed' };
  } catch (err) {
    return { success: false, message: String(err) };
  }
}

export async function deleteEndpoint(endpointId: string): Promise<{ success: boolean; message: string }> {
  try {
    const res = await fetch(`${API_BASE}/endpoints/${endpointId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    const data = await res.json();
    return { success: res.ok, message: data.message || 'Endpoint deleted' };
  } catch (err) {
    return { success: false, message: String(err) };
  }
}
