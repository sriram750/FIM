import React from 'react';
import { 
  Server, 
  Activity, 
  AlertTriangle, 
  Database, 
  Cpu, 
  HardDrive, 
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import { SystemHealthData } from '../types';

interface DashboardProps {
  health: SystemHealthData | null;
  onRefresh: () => void;
  isLoading: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({ health, onRefresh, isLoading }) => {
  return (
    <div className="space-y-6">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Overview</h2>
          <p className="text-xs text-gray-400">Enterprise File Integrity & Windows Auditing Telemetry</p>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#1A2234] hover:bg-[#26324D] text-xs font-semibold text-gray-200 border border-[#1F293D] transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-400' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Endpoints */}
        <div className="glass-panel rounded-xl p-5 border border-[#1F293D]">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-gray-400">Enrolled Endpoints</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Server className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">0</span>
            <span className="text-xs text-gray-400 font-medium">Nodes</span>
          </div>
          <div className="mt-2 text-[11px] text-gray-400 flex items-center justify-between">
            <span>Online: <b className="text-emerald-400">0</b></span>
            <span>Unhealthy: <b className="text-rose-400">0</b></span>
            <span>Offline: <b className="text-gray-400">0</b></span>
          </div>
        </div>

        {/* Card 2: File Events */}
        <div className="glass-panel rounded-xl p-5 border border-[#1F293D]">
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
        <div className="glass-panel rounded-xl p-5 border border-[#1F293D]">
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
            <span>Redis: {health?.services.redis?.status || 'idle'}</span>
          </div>
        </div>
      </div>

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

      {/* Operational Empty State / Guidance */}
      <div className="glass-panel rounded-xl p-8 border border-[#1F293D] text-center">
        <div className="w-12 h-12 mx-auto rounded-full bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-3">
          <Server className="w-6 h-6" />
        </div>
        <h4 className="text-base font-semibold text-white">No Windows Endpoints Enrolled</h4>
        <p className="text-xs text-gray-400 max-w-md mx-auto mt-1">
          Deploy the FIM Windows Agent to your endpoints using Group Policy or the enrollment token. Telemetry will automatically begin streaming upon enrollment.
        </p>
      </div>
    </div>
  );
};
