import React, { useState } from 'react';
import { FileSearch, Search } from 'lucide-react';

export const FileExplorerPage: React.FC = () => {
  const [query, setQuery] = useState('');

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">File Integrity Explorer</h2>
        <p className="text-xs text-gray-400">Baseline records, cryptographic hashes, and drift verification</p>
      </div>

      <div className="flex items-center gap-3 glass-panel p-3 rounded-xl border border-[#1F293D]">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by file path or SHA-256 hash..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-[#0B0F17] border border-[#1F293D] rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white rounded-lg transition">
          Search Baselines
        </button>
      </div>

      <div className="glass-panel rounded-xl border border-[#1F293D] p-8 text-center">
        <FileSearch className="w-8 h-8 text-gray-600 mx-auto mb-2" />
        <span className="font-medium text-gray-300 text-sm block">No Baseline Records Indexed</span>
        <span className="text-[11px] text-gray-500 mt-1 block max-w-sm mx-auto">
          When endpoints complete their initial full scan, verified SHA-256 hashes and timestamp snapshots will be listed here.
        </span>
      </div>
    </div>
  );
};
