import React from 'react';
import { Users, Key, Database } from 'lucide-react';

export const AdministrationPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">System Administration</h2>
        <p className="text-xs text-gray-400">Manage user roles, agent enrollment keys, retention schedules, and audit trails</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* User Management */}
        <div className="glass-panel p-5 rounded-xl border border-[#1F293D]">
          <div className="p-2.5 w-fit rounded-lg bg-blue-500/10 text-blue-400 mb-3">
            <Users className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-white">Users & RBAC</h3>
          <p className="text-xs text-gray-400 mt-1">Configure security analyst access, multi-factor authentication, and permissions.</p>
        </div>

        {/* Enrollment Keys */}
        <div className="glass-panel p-5 rounded-xl border border-[#1F293D]">
          <div className="p-2.5 w-fit rounded-lg bg-emerald-500/10 text-emerald-400 mb-3">
            <Key className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-white">Agent Enrollment Keys</h3>
          <p className="text-xs text-gray-400 mt-1">Generate and rotate deployment tokens for Windows clients and server clusters.</p>
        </div>

        {/* Retention & Storage */}
        <div className="glass-panel p-5 rounded-xl border border-[#1F293D]">
          <div className="p-2.5 w-fit rounded-lg bg-purple-500/10 text-purple-400 mb-3">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-white">Retention & Archival</h3>
          <p className="text-xs text-gray-400 mt-1">Define PostgreSQL event table partitioning and OpenSearch index lifecycle management.</p>
        </div>
      </div>
    </div>
  );
};
