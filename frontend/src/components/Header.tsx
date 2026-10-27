import React from 'react';
import { Bell, UserCheck, ShieldAlert, Wifi, LogOut } from 'lucide-react';
import { SystemHealthData } from '../types';
import { AuthUser } from '../api/auth';

interface HeaderProps {
  health: SystemHealthData | null;
  user: AuthUser | null;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({ health, user, onLogout }) => {
  const getStatusBadge = () => {
    if (!health) {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700">
          <Wifi className="w-3.5 h-3.5 animate-spin" /> Connecting...
        </span>
      );
    }
    if (health.status === 'healthy') {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Cluster Healthy
        </span>
      );
    }
    if (health.status === 'degraded') {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-950/60 text-amber-400 border border-amber-800/60">
          <span className="w-2 h-2 rounded-full bg-amber-400"></span>
          Cluster Degraded
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-950/60 text-rose-400 border border-rose-800/60">
        <ShieldAlert className="w-3.5 h-3.5" />
        Cluster Offline
      </span>
    );
  };

  return (
    <header className="h-16 bg-[#111827] border-b border-[#1F293D] flex items-center justify-between px-6 z-10">
      <div className="flex items-center gap-4">
        {getStatusBadge()}
        {health?.services && (
          <div className="hidden lg:flex items-center gap-3 text-xs text-gray-400">
            <span>DB: <b className="text-gray-200">{health.services.database?.status || 'unknown'}</b></span>
            <span>•</span>
            <span>Redis: <b className="text-gray-200">{health.services.redis?.status || 'unknown'}</b></span>
            <span>•</span>
            <span>OpenSearch: <b className="text-gray-200">{health.services.opensearch?.status || 'unknown'}</b></span>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        {/* Alerts Bell */}
        <button className="relative p-2 rounded-lg text-gray-400 hover:text-white hover:bg-[#1A2234] transition">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full"></span>
        </button>

        {/* User Pill & Role */}
        <div className="flex items-center gap-3 pl-3 border-l border-[#1F293D]">
          <div className="w-8 h-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-xs">
            {user?.full_name ? user.full_name.substring(0, 2).toUpperCase() : <UserCheck className="w-4 h-4" />}
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-semibold text-gray-200 flex items-center gap-2">
              <span>{user?.full_name || 'Security User'}</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-950 text-blue-300 border border-blue-800">
                {user?.role || 'Analyst'}
              </span>
            </div>
            <div className="text-[10px] text-gray-400">{user?.email || 'admin@fim.local'}</div>
          </div>

          {/* Logout Button */}
          <button
            onClick={onLogout}
            title="Log out of session"
            className="p-1.5 rounded-lg text-gray-400 hover:text-rose-400 hover:bg-[#1A2234] transition ml-1"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
