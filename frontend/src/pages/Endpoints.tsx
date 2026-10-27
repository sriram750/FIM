import React, { useState } from 'react';
import { 
  Server, 
  Search, 
  Plus, 
  Download, 
  Copy, 
  Check, 
  ShieldCheck, 
  Layers, 

  X,
  FileCode,
  FolderLock
} from 'lucide-react';
import { EndpointItem } from '../types';

export const EndpointsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [enrollTab, setEnrollTab] = useState<'windows' | 'linux'>('windows');
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  const [endpoints] = useState<EndpointItem[]>([]);

  const serverUrl = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000' 
    : window.location.origin;

  const enrollmentToken = 'change_this_enrollment_token_secret';

  const windowsPowerShellCmd = `& "C:\\Temp\\FIM\\agent-windows\\installer\\install.ps1" -ServerUrl "${serverUrl}" -EnrollmentToken "${enrollmentToken}"`;
  const linuxCurlCmd = `curl -sSL ${serverUrl}/api/v1/agents/download/linux-script | sudo bash -s -- --server "${serverUrl}" --token "${enrollmentToken}"`;

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(key);
    setTimeout(() => setCopiedCmd(null), 2500);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">Endpoint Inventory</h2>
          <p className="text-xs text-gray-400">Manage monitored Windows & Linux endpoints and deploy agents</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setShowEnrollModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/30 transition"
          >
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
            placeholder="Filter by Hostname, IP address, or Domain..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0B0F17] border border-[#1F293D] rounded-lg pl-9 pr-3 py-1.5 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <select 
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-[#0B0F17] border border-[#1F293D] rounded-lg px-3 py-1.5 text-xs text-gray-300 focus:outline-none focus:border-blue-500"
        >
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
              <th className="py-3 px-4">OS Platform</th>
              <th className="py-3 px-4">IP Address</th>
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
                    <span className="text-[11px] text-gray-500 mt-1 max-w-sm">
                      Click <b>Enroll New Endpoint</b> above to view the Windows (.exe / .msi) or Linux agent installation instructions.
                    </span>
                  </div>
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      {/* ENROLLMENT & INSTALLATION MODAL */}
      {showEnrollModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="glass-panel rounded-2xl border border-[#1F293D] max-w-2xl w-full p-6 shadow-2xl space-y-5 my-8">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-[#1F293D] pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Layers className="w-5 h-5 text-blue-400" />
                  Install & Enroll FIM Agent
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">Deploy the file integrity monitoring agent to client computers</p>
              </div>
              <button 
                onClick={() => setShowEnrollModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-[#1A2234] transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* OS Tab Selector */}
            <div className="flex items-center gap-2 p-1 bg-[#0B0F17] rounded-xl border border-[#1F293D] w-fit">
              <button
                onClick={() => setEnrollTab('windows')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                  enrollTab === 'windows' 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <span>Windows (.exe / .msi / PS1)</span>
              </button>
              <button
                onClick={() => setEnrollTab('linux')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                  enrollTab === 'linux' 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <span>Linux (curl / bash / systemd)</span>
              </button>
            </div>

            {/* WINDOWS TAB CONTENT */}
            {enrollTab === 'windows' && (
              <div className="space-y-4 text-xs">
                {/* Step 1: Download Installers */}
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-3">
                  <span className="font-semibold text-gray-200 block">Step 1: Download Windows Agent Package</span>
                  <div className="flex flex-wrap items-center gap-3">
                    <a
                      href="/api/v1/agents/download/windows-exe"
                      download="fim-agent.exe"
                      className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#1A2234] hover:bg-[#26324D] text-gray-200 border border-[#1F293D] font-medium transition"
                    >
                      <Download className="w-4 h-4 text-blue-400" />
                      Download Standalone (.exe)
                    </a>
                    <a
                      href="/api/v1/agents/download/windows-msi"
                      download="fim-agent-installer.msi"
                      className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#1A2234] hover:bg-[#26324D] text-gray-200 border border-[#1F293D] font-medium transition"
                    >
                      <Download className="w-4 h-4 text-purple-400" />
                      Download Installer (.msi)
                    </a>
                  </div>
                </div>

                {/* Step 2: One-Line PowerShell Command */}
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-200">Step 2: Automated PowerShell Installation (Run as Administrator)</span>
                    <button
                      onClick={() => handleCopy(windowsPowerShellCmd, 'win_cmd')}
                      className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-medium text-[11px]"
                    >
                      {copiedCmd === 'win_cmd' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCmd === 'win_cmd' ? 'Copied Command!' : 'Copy Command'}</span>
                    </button>
                  </div>
                  <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-emerald-400 overflow-x-auto whitespace-pre-wrap">
                    {windowsPowerShellCmd}
                  </pre>
                  <p className="text-[11px] text-gray-400">
                    Installs the background Windows Service (`FIMEnterpriseAgent`), creates the local ACID SQLite spool, and enables Event ID 4663 auditing.
                  </p>
                </div>

                {/* Step 3: SACL Security Auditing Note */}
                <div className="p-3.5 rounded-xl bg-blue-950/40 border border-blue-900/60 text-blue-300 text-[11px] flex items-start gap-2.5">
                  <FolderLock className="w-4 h-4 flex-shrink-0 mt-0.5 text-blue-400" />
                  <div>
                    <span className="font-semibold block text-blue-200">Windows User Attribution (SACLs):</span>
                    For sensitive folders (e.g. `C:\Finance`), apply an Auditing SACL for `Everyone` (Success/Fail on Create, Write, Delete) so Windows generates Event ID 4663 to attribute actor SIDs.
                  </div>
                </div>
              </div>
            )}

            {/* LINUX TAB CONTENT */}
            {enrollTab === 'linux' && (
              <div className="space-y-4 text-xs">
                {/* Step 1: One-Line Curl Command */}
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-200">Single-Line Terminal Installation (curl + sudo bash)</span>
                    <button
                      onClick={() => handleCopy(linuxCurlCmd, 'linux_cmd')}
                      className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-medium text-[11px]"
                    >
                      {copiedCmd === 'linux_cmd' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCmd === 'linux_cmd' ? 'Copied Command!' : 'Copy Command'}</span>
                    </button>
                  </div>
                  <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-cyan-400 overflow-x-auto whitespace-pre-wrap">
                    {linuxCurlCmd}
                  </pre>
                  <p className="text-[11px] text-gray-400">
                    Configures Python virtualenv in `/opt/fim-agent`, generates local SQLite spool in `/var/lib/fim-agent`, and starts the `fim-agent.service` systemd unit.
                  </p>
                </div>

                {/* Step 2: Download Raw Script */}
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-gray-200 block">Manual Deployment Script</span>
                    <span className="text-[11px] text-gray-400">Download the shell script for offline or air-gapped installation</span>
                  </div>
                  <a
                    href="/api/v1/agents/download/linux-script"
                    download="install.sh"
                    className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-[#1A2234] hover:bg-[#26324D] text-gray-200 border border-[#1F293D] font-medium transition"
                  >
                    <FileCode className="w-4 h-4 text-cyan-400" />
                    Download install.sh
                  </a>
                </div>
              </div>
            )}

            {/* Modal Footer */}
            <div className="border-t border-[#1F293D] pt-4 flex items-center justify-between text-[11px] text-gray-400">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Zero-Trust Enrollment Secret Protected
              </span>
              <button
                onClick={() => setShowEnrollModal(false)}
                className="px-4 py-2 rounded-xl bg-[#1A2234] hover:bg-[#26324D] text-gray-200 font-semibold transition"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};
