export type NavigationTab = 
  | 'overview'
  | 'endpoints'
  | 'policies'
  | 'file-explorer'
  | 'event-explorer'
  | 'alerts'
  | 'reports'
  | 'admin';

export interface ServiceHealthItem {
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency_ms?: number;
  details?: Record<string, unknown>;
}

export interface SystemHealthData {
  status: 'healthy' | 'degraded' | 'unhealthy';
  app_name: string;
  version: string;
  environment: string;
  timestamp: string;
  services: Record<string, ServiceHealthItem>;
}

export interface EndpointItem {
  id: string;
  hostname: string;
  domain?: string;
  ip_address?: string;
  os_name?: string;
  os_version?: string;
  agent_version: string;
  status: 'online' | 'offline' | 'unhealthy' | 'quarantined' | 'revoked';
  last_seen: string;
  is_isolated: boolean;
}

export interface FileEventItem {
  id: string;
  endpoint_hostname: string;
  event_type: 'file_created' | 'file_modified' | 'file_deleted' | 'file_renamed' | 'integrity_mismatch';
  file_path: string;
  old_file_path?: string;
  sha256_hash?: string;
  event_timestamp: string;
  attributed_user: string;
  correlation_status: 'CONFIRMED' | 'PROBABLE' | 'AMBIGUOUS' | 'UNKNOWN';
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
}

export interface AlertItem {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'open' | 'investigating' | 'resolved' | 'closed';
  endpoint_hostname: string;
  first_triggered_at: string;
  last_triggered_at: string;
  event_count: number;
}
