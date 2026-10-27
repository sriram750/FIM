import React from 'react';
import { Plus, FolderCheck } from 'lucide-react';

export const PoliciesPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Monitoring Policies</h2>
          <p className="text-xs text-gray-400">Configure monitored directories, exclusions, and hashing triggers</p>
        </div>
        <button className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/20 transition">
          <Plus className="w-4 h-4" />
          Create Policy
        </button>
      </div>

      {/* Default Enterprise Policy Card */}
      <div className="glass-panel rounded-xl p-5 border border-[#1F293D] space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white">Default Windows Enterprise Baseline</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-950 text-blue-400 border border-blue-800">
                v1 • Active
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Monitors critical system directories, executables, scripts, and sensitive shares.</p>
          </div>
          <div className="text-right text-xs text-gray-400">
            Assigned: <b className="text-white">All Endpoints</b>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 border-t border-[#1F293D] text-xs">
          <div>
            <span className="font-semibold text-gray-300 block mb-1">Monitored Paths</span>
            <ul className="space-y-1 font-mono text-[11px] text-gray-400">
              <li className="flex items-center gap-1.5"><FolderCheck className="w-3.5 h-3.5 text-blue-400" /> C:\Windows\System32\drivers\etc (Recursive)</li>
              <li className="flex items-center gap-1.5"><FolderCheck className="w-3.5 h-3.5 text-blue-400" /> C:\Program Files\Common Files (Recursive)</li>
              <li className="flex items-center gap-1.5"><FolderCheck className="w-3.5 h-3.5 text-blue-400" /> D:\EnterpriseShares\Confidential (Recursive)</li>
            </ul>
          </div>
          <div>
            <span className="font-semibold text-gray-300 block mb-1">Configuration</span>
            <ul className="space-y-1 text-gray-400">
              <li>• SHA-256 Hashing: <b className="text-emerald-400">Enabled (Create & Modify)</b></li>
              <li>• Max File Size: <b className="text-gray-200">100 MB</b></li>
              <li>• Windows Security Auditing: <b className="text-emerald-400">Enabled (Object Access 4663)</b></li>
              <li>• Scan Reconciliation Interval: <b className="text-gray-200">3600 seconds</b></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
