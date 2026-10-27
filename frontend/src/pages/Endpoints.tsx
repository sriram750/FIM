import React, { useState } from 'react';
import { Server, Search, Plus } from 'lucide-react';
import { EndpointItem } from '../types';

export const EndpointsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [endpoints] = useState<EndpointItem[]>([]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Endpoint Inventory</h2>
          <p className="text-xs text-gray-400">Manage enrolled Windows clients and file servers</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/20 transition">
            <Plus className="w-4 h-4" />
            Enroll New Endpoint
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex items-center gap-3 glass-panel p-3 rounded-xl border border-[#1F293D]">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter by Hostname, IP, or Domain..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0B0F17] border border-[#1F293D] rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <select className="bg-[#0B0F17] border border-[#1F293D] rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-blue-500">
          <option value="all">All Statuses</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
          <option value="unhealthy">Unhealthy</option>
        </select>
      </div>

      {/* Endpoints Table */}
      <div className="glass-panel rounded-xl border border-[#1F293D] overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-[#1A2234] border-b border-[#1F293D] text-gray-400 uppercase tracking-wider font-semibold">
              <th className="py-3 px-4">Hostname</th>
              <th className="py-3 px-4">IP Address</th>
              <th className="py-3 px-4">OS Version</th>
              <th className="py-3 px-4">Agent Version</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Last Seen</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1F293D]">
            {endpoints.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-gray-400">
                  <div className="flex flex-col items-center justify-center">
                    <Server className="w-8 h-8 text-gray-600 mb-2" />
                    <span className="font-medium text-gray-300">No registered endpoints found</span>
                    <span className="text-[11px] text-gray-500 mt-0.5">Use the enrollment token on the Windows agent to register machines.</span>
                  </div>
                </td>
              </tr>
            ) : (
              endpoints.map((ep) => (
                <tr key={ep.id} className="hover:bg-[#1A2234]/50 transition">
                  <td className="py-3 px-4 font-mono font-medium text-white">{ep.hostname}</td>
                  <td className="py-3 px-4 text-gray-300 font-mono">{ep.ip_address || '—'}</td>
                  <td className="py-3 px-4 text-gray-300">{ep.os_version || 'Windows'}</td>
                  <td className="py-3 px-4 text-gray-300 font-mono">{ep.agent_version}</td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-950 text-emerald-400 border border-emerald-800">
                      {ep.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-400">{ep.last_seen}</td>
                  <td className="py-3 px-4 text-right">
                    <button className="text-blue-400 hover:text-blue-300 font-medium">Manage</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
