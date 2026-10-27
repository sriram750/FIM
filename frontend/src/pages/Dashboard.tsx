import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Activity, 
  AlertTriangle, 
  Database, 
  Cpu, 
  HardDrive, 
  ShieldCheck,
  RefreshCw,
  ArrowRight,
  ExternalLink,
  Laptop
} from 'lucide-react';
import { SystemHealthData, EndpointItem, NavigationTab } from '../types';
import { fetchEndpoints } from '../api/endpoints';

interface DashboardProps {
  health: SystemHealthData | null;
  onRefresh: () => void;
  isLoading: boolean;
  onNavigate?: (tab: NavigationTab) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ health, onRefresh, isLoading, onNavigate }) => {
  const [endpoints, setEndpoints] = useState<EndpointItem[]>([]);
  const [loadingEndpoints, setLoadingEndpoints] = useState(false);

  const loadData = async () => {
    setLoadingEndpoints(true);
    const data = await fetchEndpoints();
    setEndpoints(data.items);
    setLoadingEndpoints(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefreshAll = () => {
    onRefresh();
    loadData();
  };

  const totalEndpoints = endpoints.length;
  const onlineCount = endpoints.filter(e => e.status === 'online').length;
  const unhealthyCount = endpoints.filter(e => e.status === 'unhealthy').length;
  const offlineCount = endpoints.filter(e => e.status === 'offline' || e.status === 'revoked').length;

  return (
    <div className="space-y-6">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Overview</h2>
          <p className="text-xs text-gray-400">Enterprise File Integrity & Windows Auditing Telemetry</p>
        </div>
        <button
          onClick={handleRefreshAll}
          disabled={isLoading || loadingEndpoints}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#1A2234] hover:bg-[#26324D] text-xs font-semibold text-gray-200 border border-[#1F293D] transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${(isLoading || loadingEndpoints) ? 'animate-spin text-blue-400' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Endpoints */}
        <div 
          onClick={() => onNavigate && onNavigate('endpoints')}
          className="glass-panel rounded-xl p-5 border border-[#1F293D] hover:border-blue-500/40 transition cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Enrolled Endpoints</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Server className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{totalEndpoints}</span>
            <span className="text-xs text-gray-400 font-medium">Nodes</span>
          </div>
          <div className="mt-2 text-[11px] text-gray-400 flex items-center justify-between">
            <span>Online: <b className="text-emerald-400">{onlineCount}</b></span>
            <span>Unhealthy: <b className="text-rose-400">{unhealthyCount}</b></span>
            <span>Offline: <b className="text-gray-400">{offlineCount}</b></span>
          </div>
        </div>

        {/* Card 2: File Events */}
        <div 
          onClick={() => onNavigate && onNavigate('event-explorer')}
          className="glass-panel rounded-xl p-5 border border-[#1F293D] hover:border-cyan-500/40 transition cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">File Events (24h)</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">0</span>
            <span className="text-xs text-gray-400 font-medium">Events</span>
          </div>
          <div className="mt-2 text-[11px] text-gray-400 flex items-center justify-between">
            <span>Created: 0</span>
            <span>Modified: 0</span>
            <span>Deleted: 0</span>
          </div>
        </div>

        {/* Card 3: Active Alerts */}
        <div 
          onClick={() => onNavigate && onNavigate('alerts')}
          className="glass-panel rounded-xl p-5 border border-[#1F293D] hover:border-rose-500/40 transition cursor-pointer"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Critical / High Alerts</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">0</span>
            <span className="text-xs text-emerald-400 font-medium">Clear</span>
          </div>
          <div className="mt-2 text-[11px] text-gray-400 flex items-center justify-between">
            <span>Open: 0</span>
            <span>Investigating: 0</span>
            <span>Resolved: 0</span>
          </div>
        </div>

        {/* Card 4: Ingestion Backlog */}
        <div className="glass-panel rounded-xl p-5 border border-[#1F293D]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Queue & Indexing</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">0</span>
            <span className="text-xs text-gray-400 font-medium">Lag ms</span>
          </div>
          <div className="mt-2 text-[11px] text-gray-400 flex items-center justify-between">
            <span>Queue Depth: 0</span>
            <span>Redis: {health?.services?.redis?.status || 'idle'}</span>
          </div>
        </div>
      </div>

      {/* ACTIVE MONITORED ENDPOINTS SECTION */}
      {totalEndpoints > 0 ? (
        <div className="glass-panel rounded-xl border border-[#1F293D] p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Laptop className="w-4 h-4 text-blue-400" />
              <h3 className="text-sm font-semibold text-white">
                Active Monitored Endpoints ({totalEndpoints})
              </h3>
            </div>
            {onNavigate && (
              <button
                onClick={() => onNavigate('endpoints')}
                className="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition"
              >
                <span>View Full Inventory</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {endpoints.map((ep) => (
              <div 
                key={ep.id}
                className="p-4 rounded-xl bg-[#111827] border border-[#1F293D] hover:border-blue-500/30 transition flex flex-col justify-between space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-white">{ep.hostname}</h4>
                    <p className="text-[11px] text-gray-400">{ep.domain || 'WORKGROUP'}</p>
                  </div>
                  <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                    ep.status === 'online'
                      ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                      : 'bg-gray-800 text-gray-400 border border-gray-700'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${ep.status === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-gray-400'}`} />
                    {ep.status.toUpperCase()}
                  </span>
                </div>

                <div className="pt-2 border-t border-[#1F293D]/60 text-[11px] text-gray-400 space-y-1">
                  <div className="flex justify-between">
                    <span>OS Platform:</span>
                    <span className="text-gray-200 font-medium">{ep.os_name || 'Windows'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Agent Version:</span>
                    <span className="text-gray-200 font-mono">v{ep.agent_version}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Last Check-in:</span>
                    <span className="text-gray-300 font-mono text-[10px]">
                      {new Date(ep.last_seen).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* Empty State / Guidance */
        <div className="glass-panel rounded-xl p-8 border border-[#1F293D] text-center space-y-3">
          <div className="w-12 h-12 mx-auto rounded-full bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Server className="w-6 h-6" />
          </div>
          <h4 className="text-base font-semibold text-white">No Windows Endpoints Enrolled</h4>
          <p className="text-xs text-gray-400 max-w-md mx-auto">
            Deploy the FIM Windows Agent to your endpoints using Group Policy or the enrollment token. Telemetry will automatically begin streaming upon enrollment.
          </p>
          {onNavigate && (
            <button
              onClick={() => onNavigate('endpoints')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/30 transition"
            >
              <span>View Agent Installation Steps</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Cluster Infrastructure Health Table */}
      <div className="glass-panel rounded-xl p-5 border border-[#1F293D]">
        <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-blue-400" />
          Infrastructure Health & Service Topology
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Postgres Box */}
          <div className="p-4 rounded-lg bg-[#111827] border border-[#1F293D] flex items-start justify-between">
            <div>
              <div className="text-xs font-semibold text-gray-200 flex items-center gap-2">
                <Database className="w-4 h-4 text-blue-400" /> PostgreSQL 16 Primary
              </div>
              <p className="text-[11px] text-gray-400 mt-1">Authoritative configuration & baselines</p>
              <div className="mt-3 text-xs font-mono text-gray-300">
                Latency: <span className="text-blue-400">{health?.services?.database?.latency_ms ?? 0} ms</span>
              </div>
            </div>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
              health?.services?.database?.status === 'healthy' 
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                : 'bg-rose-950 text-rose-400 border border-rose-800'
            }`}>
              {health?.services?.database?.status || 'Unknown'}
            </span>
          </div>

          {/* Redis Box */}
          <div className="p-4 rounded-lg bg-[#111827] border border-[#1F293D] flex items-start justify-between">
            <div>
              <div className="text-xs font-semibold text-gray-200 flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-purple-400" /> Redis Streams
              </div>
              <p className="text-[11px] text-gray-400 mt-1">High-throughput ingestion buffer</p>
              <div className="mt-3 text-xs font-mono text-gray-300">
                Latency: <span className="text-purple-400">{health?.services?.redis?.latency_ms ?? 0} ms</span>
              </div>
            </div>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
              health?.services?.redis?.status === 'healthy' 
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                : 'bg-amber-950 text-amber-400 border border-amber-800'
            }`}>
              {health?.services?.redis?.status || 'Standby'}
            </span>
          </div>

          {/* OpenSearch Box */}
          <div className="p-4 rounded-lg bg-[#111827] border border-[#1F293D] flex items-start justify-between">
            <div>
              <div className="text-xs font-semibold text-gray-200 flex items-center gap-2">
                <Cpu className="w-4 h-4 text-cyan-400" /> OpenSearch 2.11
              </div>
              <p className="text-[11px] text-gray-400 mt-1">Distributed forensic search index</p>
              <div className="mt-3 text-xs font-mono text-gray-300">
                Latency: <span className="text-cyan-400">{health?.services?.opensearch?.latency_ms ?? 0} ms</span>
              </div>
            </div>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
              health?.services?.opensearch?.status === 'healthy' 
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' 
                : 'bg-amber-950 text-amber-400 border border-amber-800'
            }`}>
              {health?.services?.opensearch?.status || 'Standby'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
