import React from 'react';
import { 
  Shield, 
  LayoutDashboard, 
  Server, 
  Sliders, 
  FileSearch, 
  Activity, 
  AlertTriangle, 
  FileText, 
  Settings 
} from 'lucide-react';
import { NavigationTab } from '../types';

interface SidebarProps {
  currentTab: NavigationTab;
  onSelectTab: (tab: NavigationTab) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab }) => {
  const menuItems: { id: NavigationTab; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: 'endpoints', label: 'Endpoints', icon: <Server className="w-5 h-5" /> },
    { id: 'policies', label: 'Monitoring Policies', icon: <Sliders className="w-5 h-5" /> },
    { id: 'file-explorer', label: 'File Baselines', icon: <FileSearch className="w-5 h-5" /> },
    { id: 'event-explorer', label: 'Event Explorer', icon: <Activity className="w-5 h-5" /> },
    { id: 'alerts', label: 'Alerts & Triage', icon: <AlertTriangle className="w-5 h-5" /> },
    { id: 'reports', label: 'Compliance Reports', icon: <FileText className="w-5 h-5" /> },
    { id: 'admin', label: 'Administration', icon: <Settings className="w-5 h-5" /> },
  ];

  return (
    <aside className="w-64 bg-[#111827] border-r border-[#1F293D] flex flex-col h-screen select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-[#1F293D]">
        <div className="p-2 bg-blue-600/10 rounded-lg border border-blue-500/20 text-blue-400">
          <Shield className="w-6 h-6 text-blue-500" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-wide flex items-center gap-1.5">
            FIM <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700/50">ENTERPRISE</span>
          </h1>
          <p className="text-[11px] text-gray-400">Windows File Security</p>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
          Monitoring & Defense
        </div>
        {menuItems.map((item) => {
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                  : 'text-gray-300 hover:bg-[#1A2234] hover:text-white'
              }`}
            >
              <span className={isActive ? 'text-white' : 'text-gray-400'}>{item.icon}</span>
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-[#1F293D] text-[11px] text-gray-400 flex items-center justify-between">
        <span className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Cluster Active
        </span>
        <span className="font-mono text-gray-400">v1.0.0</span>
      </div>
    </aside>
  );
};
