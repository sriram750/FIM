import React from 'react';
import { FileText, Download, Calendar } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const reports = [
    { title: 'PCI-DSS File Integrity Audit', desc: 'Summary of critical file modifications and baseline drift records over the past 30 days.' },
    { title: 'Deleted Files & Unattributed Changes', desc: 'Listing of all file deletion events where Windows Security correlation could not attribute an actor SID.' },
    { title: 'Endpoint Agent Compliance Report', desc: 'Coverage and health report across all 500+ enrolled Windows nodes.' },
    { title: 'Executable & Script Modification Log', desc: 'Forensic log of changes to .exe, .dll, .ps1, and .bat files across protected shares.' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">Compliance & Forensic Reports</h2>
        <p className="text-xs text-gray-400">Generate and export audit-ready reports for security compliance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map((r, idx) => (
          <div key={idx} className="glass-panel p-5 rounded-xl border border-[#1F293D] flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-white">{r.title}</span>
                <FileText className="w-4 h-4 text-blue-400" />
              </div>
              <p className="text-xs text-gray-400">{r.desc}</p>
            </div>
            <div className="mt-4 pt-3 border-t border-[#1F293D] flex items-center justify-between">
              <span className="text-[11px] text-gray-500 flex items-center gap-1">
                <Calendar className="w-3 h-3" /> Past 30 Days
              </span>
              <button className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#1A2234] hover:bg-[#26324D] rounded-lg text-xs font-semibold text-gray-200 border border-[#1F293D] transition">
                <Download className="w-3.5 h-3.5" /> Export CSV
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
