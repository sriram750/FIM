import React from 'react';
import { CheckCircle2 } from 'lucide-react';

export const AlertsPage: React.FC = () => {

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Alerts & Forensic Investigations</h2>
          <p className="text-xs text-gray-400">Triage integrity drifts, bulk modifications, and unauthorized script executions</p>
        </div>
      </div>

      <div className="glass-panel rounded-xl border border-[#1F293D] p-12 text-center">
        <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
        <span className="font-semibold text-white text-sm block">No Active Security Alerts</span>
        <span className="text-[11px] text-gray-400 mt-1 block max-w-sm mx-auto">
          All monitored file baselines match their trusted state. Any rule breaches or ransomware bursts will trigger immediate triage alerts here.
        </span>
      </div>
    </div>
  );
};
