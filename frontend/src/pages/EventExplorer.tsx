import React, { useState } from 'react';
import { Activity, Search, Download } from 'lucide-react';
import { FileEventItem } from '../types';

export const EventExplorerPage: React.FC = () => {
  const [events] = useState<FileEventItem[]>([]);
  const [filterType, setFilterType] = useState('all');

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Security Event Explorer</h2>
          <p className="text-xs text-gray-400">Forensic file change stream with Windows Security user attribution</p>
        </div>
        <button className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#1A2234] hover:bg-[#26324D] text-xs font-semibold text-gray-200 border border-[#1F293D] transition">
          <Download className="w-4 h-4" />
          Export Filtered CSV
        </button>
      </div>

      {/* Filter Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 glass-panel p-3 rounded-xl border border-[#1F293D]">
        <div className="sm:col-span-2 relative">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search path, filename, hash, or user account..."
            className="w-full bg-[#0B0F17] border border-[#1F293D] rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <select 
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="bg-[#0B0F17] border border-[#1F293D] rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-blue-500"
        >
          <option value="all">All Event Types</option>
          <option value="file_created">File Created</option>
          <option value="file_modified">File Modified</option>
          <option value="file_deleted">File Deleted</option>
          <option value="file_renamed">File Renamed</option>
          <option value="integrity_mismatch">Integrity Mismatch</option>
        </select>
        <select className="bg-[#0B0F17] border border-[#1F293D] rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-blue-500">
          <option value="all">All Confidence</option>
          <option value="confirmed">CONFIRMED (Exact Handle)</option>
          <option value="probable">PROBABLE (Time Window)</option>
          <option value="ambiguous">AMBIGUOUS</option>
          <option value="unknown">UNKNOWN</option>
        </select>
      </div>

      {/* Event Grid */}
      <div className="glass-panel rounded-xl border border-[#1F293D] overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-[#1A2234] border-b border-[#1F293D] text-gray-400 uppercase tracking-wider font-semibold">
              <th className="py-3 px-4">Timestamp (UTC)</th>
              <th className="py-3 px-4">Endpoint</th>
              <th className="py-3 px-4">Event Type</th>
              <th className="py-3 px-4">File Path</th>
              <th className="py-3 px-4">SHA-256 Hash</th>
              <th className="py-3 px-4">Attributed Account</th>
              <th className="py-3 px-4">Confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1F293D]">
            {events.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-gray-400">
                  <Activity className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                  <span className="font-medium text-gray-300 block">No Ingested Events</span>
                  <span className="text-[11px] text-gray-500 mt-1 block">Live events will appear as agents detect changes.</span>
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
};
