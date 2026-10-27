import React, { useState, useEffect } from 'react';
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
  FolderLock,
  ChevronDown,
  ChevronUp,
  Terminal,
  RefreshCw,
  AlertTriangle,
  Trash2,
  ShieldAlert,
  HardDrive
} from 'lucide-react';
import { EndpointItem } from '../types';
import { fetchEndpoints, revokeEndpoint, deleteEndpoint } from '../api/endpoints';
import { getStoredAuth } from '../api/auth';

export const EndpointsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const [showInstallGuide, setShowInstallGuide] = useState(true);
  const [installTab, setInstallTab] = useState<'windows' | 'linux'>('windows');
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);
  
  const [endpoints, setEndpoints] = useState<EndpointItem[]>([]);
  const [totalEndpoints, setTotalEndpoints] = useState(0);
  const [loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const auth = getStoredAuth();
  const currentUser = auth.user;
  const isAdmin = currentUser?.is_superuser || currentUser?.role === 'Admin';
  const isAuditor = currentUser?.role === 'Auditor';

  const serverUrl = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000' 
    : window.location.origin;

  const enrollmentToken = 'change_this_enrollment_token_secret';

  const windowsPowerShellCmd = `& "C:\\Temp\\FIM\\agent-windows\\installer\\install.ps1" -ServerUrl "${serverUrl}" -EnrollmentToken "${enrollmentToken}"`;
  const windowsManualCmd = `.\\fim-agent.exe enroll --server "${serverUrl}" --token "${enrollmentToken}"\n.\\fim-agent.exe start`;
  const linuxCurlCmd = `curl -sSL ${serverUrl}/api/v1/agents/download/linux-script | sudo bash -s -- --server "${serverUrl}" --token "${enrollmentToken}"`;
  const linuxManualCmd = `chmod +x install.sh\nsudo ./install.sh --server "${serverUrl}" --token "${enrollmentToken}"`;

  const loadEndpoints = async () => {
    setLoading(true);
    const data = await fetchEndpoints(searchTerm, statusFilter);
    setEndpoints(data.items);
    setTotalEndpoints(data.total);
    setLoading(false);
  };

  useEffect(() => {
    loadEndpoints();
  }, [searchTerm, statusFilter]);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(key);
    setTimeout(() => setCopiedCmd(null), 2500);
  };

  const handleRevoke = async (id: string, hostname: string) => {
    if (!isAdmin) {
      setActionMessage({ type: 'error', text: 'RBAC: Only Admin role has permission to revoke endpoints.' });
      return;
    }
    if (!window.confirm(`Are you sure you want to revoke credentials and isolate '${hostname}'?`)) {
      return;
    }
    const res = await revokeEndpoint(id);
    if (res.success) {
      setActionMessage({ type: 'success', text: res.message });
      loadEndpoints();
    } else {
      setActionMessage({ type: 'error', text: res.message });
    }
    setTimeout(() => setActionMessage(null), 4000);
  };

  const handleDelete = async (id: string, hostname: string) => {
    if (!isAdmin) {
      setActionMessage({ type: 'error', text: 'RBAC: Only Admin role has permission to delete endpoints.' });
      return;
    }
    if (!window.confirm(`Permanently delete '${hostname}'?`)) {
      return;
    }
    const res = await deleteEndpoint(id);
    if (res.success) {
      setActionMessage({ type: 'success', text: res.message });
      loadEndpoints();
    } else {
      setActionMessage({ type: 'error', text: res.message });
    }
    setTimeout(() => setActionMessage(null), 4000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold text-white tracking-tight">Endpoint Inventory</h2>
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-[#1F293D] text-gray-300 border border-[#2D3A54]">
              {totalEndpoints} {totalEndpoints === 1 ? 'Host' : 'Hosts'}
            </span>
            {currentUser && (
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider ${
                isAdmin 
                  ? 'bg-blue-950/80 text-blue-400 border border-blue-800/60' 
                  : isAuditor
                    ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                    : 'bg-cyan-950/80 text-cyan-400 border border-cyan-800/60'
              }`}>
                RBAC: {currentUser.role} {isAuditor ? '(Read-Only)' : ''}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400 mt-1">Monitor, manage, and install FIM agents on Windows and Linux endpoints</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setShowInstallGuide(!showInstallGuide)}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#1A2234] hover:bg-[#25324D] border border-[#1F293D] text-xs font-semibold text-gray-200 transition"
          >
            <Terminal className="w-3.5 h-3.5 text-blue-400" />
            <span>{showInstallGuide ? 'Hide Install Guide' : 'Show Install Guide'}</span>
            {showInstallGuide ? <ChevronUp className="w-3.5 h-3.5 text-gray-400" /> : <ChevronDown className="w-3.5 h-3.5 text-gray-400" />}
          </button>

          <button 
            onClick={() => setShowEnrollModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white shadow-lg shadow-blue-600/30 transition"
          >
            <Plus className="w-4 h-4" />
            Enroll New Endpoint
          </button>
        </div>
      </div>

      {/* Action Notification Alert */}
      {actionMessage && (
        <div className={`p-3.5 rounded-xl text-xs flex items-center justify-between border ${
          actionMessage.type === 'success'
            ? 'bg-emerald-950/60 border-emerald-800/60 text-emerald-300'
            : 'bg-rose-950/60 border-rose-800/60 text-rose-300'
        }`}>
          <div className="flex items-center gap-2">
            {actionMessage.type === 'success' ? <Check className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
            <span>{actionMessage.text}</span>
          </div>
          <button onClick={() => setActionMessage(null)} className="text-gray-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ========================================================================= */}
      {/* AGENT INSTALLATION STEP SECTION (AVAILABLE DIRECTLY ON THIS ENDPOINT PAGE) */}
      {/* ========================================================================= */}
      {showInstallGuide && (
        <div className="glass-panel rounded-2xl border border-blue-500/20 bg-gradient-to-b from-[#111827]/90 to-[#0B0F17]/90 p-5 shadow-2xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#1F293D] pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-blue-600/20 border border-blue-500/30 text-blue-400">
                <Layers className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                  Agent Installation & Deployment Steps
                  <span className="px-2 py-0.5 rounded text-[10px] bg-blue-900/50 text-blue-300 border border-blue-700/50">
                    Production Ready
                  </span>
                </h3>
                <p className="text-[11px] text-gray-400">Select target operating system to view agent binaries and setup commands</p>
              </div>
            </div>

            {/* OS Tabs */}
            <div className="flex items-center gap-1.5 p-1 bg-[#0B0F17] rounded-xl border border-[#1F293D]">
              <button
                onClick={() => setInstallTab('windows')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                  installTab === 'windows' 
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <span>Windows (.exe / .msi)</span>
              </button>
              <button
                onClick={() => setInstallTab('linux')}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                  installTab === 'linux' 
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <span>Linux (install.sh / curl)</span>
              </button>
            </div>
          </div>

          {/* WINDOWS TAB CONTENT */}
          {installTab === 'windows' && (
            <div className="space-y-4">
              {/* Step 1: Download Windows Packages */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] flex items-center justify-between hover:border-blue-500/40 transition">
                  <div className="space-y-1">
                    <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                      <HardDrive className="w-4 h-4 text-blue-400" />
                      Windows Standalone Binary (.exe)
                    </span>
                    <p className="text-[11px] text-gray-400">Compiled single-file agent (`fim-agent.exe` ~12 MB) with zero dependencies</p>
                  </div>
                  <a
                    href="/api/v1/agents/download/windows-exe"
                    download="fim-agent.exe"
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md transition ml-3 flex-shrink-0"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download .exe
                  </a>
                </div>

                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] flex items-center justify-between hover:border-purple-500/40 transition">
                  <div className="space-y-1">
                    <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-purple-400" />
                      Windows Installer Package (.msi)
                    </span>
                    <p className="text-[11px] text-gray-400">Microsoft Installer (`fim-agent-installer.msi`) for Group Policy (GPO) deployment</p>
                  </div>
                  <a
                    href="/api/v1/agents/download/windows-msi"
                    download="fim-agent-installer.msi"
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold shadow-md transition ml-3 flex-shrink-0"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download .msi
                  </a>
                </div>
              </div>

              {/* Step 2: Automated PowerShell Setup */}
              <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center text-xs font-bold">1</span>
                    <span className="text-xs font-semibold text-gray-200">
                      Automated PowerShell Installation (Run as Administrator)
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopy(windowsPowerShellCmd, 'win_ps_cmd')}
                    className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-medium text-xs bg-[#1A2234] px-2.5 py-1 rounded-lg border border-[#1F293D] transition"
                  >
                    {copiedCmd === 'win_ps_cmd' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedCmd === 'win_ps_cmd' ? 'Copied Command!' : 'Copy Script'}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-emerald-400 overflow-x-auto whitespace-pre-wrap">
                  {windowsPowerShellCmd}
                </pre>
                <p className="text-[11px] text-gray-400 leading-relaxed">
                  Registers background service <code className="text-gray-300">FIMEnterpriseAgent</code>, sets up SQLite WAL spool in <code className="text-gray-300">C:\ProgramData\FIM\spool.db</code>, and configures recovery parameters.
                </p>
              </div>

              {/* Step 3: Standalone CLI Manual Commands */}
              <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-blue-600/30 text-blue-400 flex items-center justify-center text-xs font-bold">2</span>
                    <span className="text-xs font-semibold text-gray-200">
                      Manual CLI Enrollment & Foreground Execution
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopy(windowsManualCmd, 'win_man_cmd')}
                    className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-medium text-xs bg-[#1A2234] px-2.5 py-1 rounded-lg border border-[#1F293D] transition"
                  >
                    {copiedCmd === 'win_man_cmd' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedCmd === 'win_man_cmd' ? 'Copied Command!' : 'Copy CLI'}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-cyan-400 overflow-x-auto whitespace-pre-wrap">
                  {windowsManualCmd}
                </pre>
              </div>

              {/* SACL Security Auditing Callout */}
              <div className="p-3.5 rounded-xl bg-blue-950/40 border border-blue-900/60 text-blue-300 text-[11px] flex items-start gap-2.5">
                <FolderLock className="w-4 h-4 flex-shrink-0 mt-0.5 text-blue-400" />
                <div>
                  <span className="font-semibold block text-blue-200">Windows Security Auditing & SACL Configuration:</span>
                  To capture actor usernames (Event ID 4663), enable Object Access Auditing via Local Security Policy (`auditpol /set /subcategory:"File System" /success:enable`) and apply a Success/Failure SACL for `Everyone` on monitored folders.
                </div>
              </div>
            </div>
          )}

          {/* LINUX TAB CONTENT */}
          {installTab === 'linux' && (
            <div className="space-y-4">
              {/* Step 1: Single-Line Curl Script */}
              <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-cyan-600/30 text-cyan-400 flex items-center justify-center text-xs font-bold">1</span>
                    <span className="text-xs font-semibold text-gray-200">
                      Single-Line Linux Installation (curl + sudo bash)
                    </span>
                  </div>
                  <button
                    onClick={() => handleCopy(linuxCurlCmd, 'linux_curl_cmd')}
                    className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 font-medium text-xs bg-[#1A2234] px-2.5 py-1 rounded-lg border border-[#1F293D] transition"
                  >
                    {copiedCmd === 'linux_curl_cmd' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedCmd === 'linux_curl_cmd' ? 'Copied Command!' : 'Copy Command'}</span>
                  </button>
                </div>
                <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-cyan-400 overflow-x-auto whitespace-pre-wrap">
                  {linuxCurlCmd}
                </pre>
                <p className="text-[11px] text-gray-400 leading-relaxed">
                  Downloads <code className="text-gray-300">install.sh</code>, installs python3-venv/watchdog, creates SQLite spool in <code className="text-gray-300">/var/lib/fim-agent</code>, and registers the <code className="text-gray-300">fim-agent.service</code> systemd daemon.
                </p>
              </div>

              {/* Step 2: Download Shell Script for Air-Gapped Systems */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] flex items-center justify-between hover:border-cyan-500/40 transition">
                  <div className="space-y-1">
                    <span className="text-xs font-semibold text-white flex items-center gap-1.5">
                      <Terminal className="w-4 h-4 text-cyan-400" />
                      Download Linux Installer Script (`install.sh`)
                    </span>
                    <p className="text-[11px] text-gray-400">Self-contained Bash installer for offline servers & custom packaging</p>
                  </div>
                  <a
                    href="/api/v1/agents/download/linux-script"
                    download="install.sh"
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold shadow-md transition ml-3 flex-shrink-0"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download Script
                  </a>
                </div>

                {/* Step 3: Manual Execution */}
                <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-gray-200">Manual Script Execution</span>
                    <button
                      onClick={() => handleCopy(linuxManualCmd, 'linux_man_cmd')}
                      className="text-cyan-400 hover:text-cyan-300 text-xs font-medium"
                    >
                      {copiedCmd === 'linux_man_cmd' ? 'Copied' : 'Copy'}
                    </button>
                  </div>
                  <pre className="p-2.5 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-gray-300 overflow-x-auto whitespace-pre-wrap">
                    {linuxManualCmd}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

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
          <option value="revoked">Revoked</option>
        </select>
        <button
          onClick={loadEndpoints}
          className="p-2 rounded-lg bg-[#1A2234] hover:bg-[#25324D] border border-[#1F293D] text-gray-300 transition"
          title="Refresh Endpoints"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-blue-400' : ''}`} />
        </button>
      </div>

      {/* Endpoints Table */}
      <div className="glass-panel rounded-xl border border-[#1F293D] overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-[#1A2234] border-b border-[#1F293D] text-gray-400 uppercase tracking-wider font-semibold">
              <th className="py-3 px-4">Hostname</th>
              <th className="py-3 px-4">Platform</th>
              <th className="py-3 px-4">IP Address</th>
              <th className="py-3 px-4">Agent Version</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">Last Seen</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1F293D]">
            {loading ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-gray-400">
                  <div className="flex flex-col items-center justify-center">
                    <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mb-2" />
                    <span className="text-xs">Loading endpoints inventory...</span>
                  </div>
                </td>
              </tr>
            ) : endpoints.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-12 text-center text-gray-400">
                  <div className="flex flex-col items-center justify-center">
                    <Server className="w-8 h-8 text-gray-600 mb-2" />
                    <span className="font-medium text-gray-300">No registered endpoints found</span>
                    <span className="text-[11px] text-gray-500 mt-1 max-w-sm">
                      Follow the <b>Agent Installation Steps</b> above to deploy and enroll your first Windows or Linux endpoint.
                    </span>
                  </div>
                </td>
              </tr>
            ) : (
              endpoints.map((ep) => (
                <tr key={ep.id} className="hover:bg-[#1A2234]/50 transition">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-white">{ep.hostname}</div>
                    {ep.domain && <div className="text-[10px] text-gray-400">{ep.domain}</div>}
                  </td>
                  <td className="py-3 px-4 text-gray-300">
                    <span className="inline-flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-blue-400" />
                      {ep.os_name || 'Windows'} {ep.os_version || ''}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-gray-300">{ep.ip_address || '—'}</td>
                  <td className="py-3 px-4 font-mono text-gray-400">v{ep.agent_version}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      ep.status === 'online'
                        ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60'
                        : ep.status === 'revoked'
                          ? 'bg-purple-950/80 text-purple-400 border border-purple-800/60'
                          : ep.status === 'unhealthy'
                            ? 'bg-rose-950/80 text-rose-400 border border-rose-800/60'
                            : 'bg-gray-800 text-gray-400 border border-gray-700'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        ep.status === 'online' ? 'bg-emerald-400 animate-pulse' : ep.status === 'revoked' ? 'bg-purple-400' : 'bg-gray-400'
                      }`} />
                      {ep.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-400 font-mono text-[11px]">
                    {new Date(ep.last_seen).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      {isAdmin ? (
                        <>
                          <button
                            onClick={() => handleRevoke(ep.id, ep.hostname)}
                            disabled={ep.status === 'revoked'}
                            className="p-1.5 rounded-lg text-amber-400 hover:text-amber-300 hover:bg-amber-950/40 border border-amber-900/40 disabled:opacity-40 transition"
                            title="Revoke Agent Credentials"
                          >
                            <ShieldAlert className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDelete(ep.id, ep.hostname)}
                            className="p-1.5 rounded-lg text-rose-400 hover:text-rose-300 hover:bg-rose-950/40 border border-rose-900/40 transition"
                            title="Delete Endpoint Record"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </>
                      ) : (
                        <span className="text-[10px] text-gray-500 italic">Read-Only</span>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ENROLLMENT POPUP MODAL (Also accessible via button) */}
      {showEnrollModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="glass-panel rounded-2xl border border-[#1F293D] max-w-2xl w-full p-6 shadow-2xl space-y-5 my-8">
            <div className="flex items-center justify-between border-b border-[#1F293D] pb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Layers className="w-5 h-5 text-blue-400" />
                  Install & Enroll FIM Agent
                </h3>
                <p className="text-xs text-gray-400 mt-0.5">Quick instructions to connect a new endpoint</p>
              </div>
              <button 
                onClick={() => setShowEnrollModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-[#1A2234] transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2">
                <span className="font-semibold text-gray-200">Windows Automated PowerShell Command:</span>
                <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-emerald-400 whitespace-pre-wrap">
                  {windowsPowerShellCmd}
                </pre>
              </div>

              <div className="p-4 rounded-xl bg-[#0B0F17] border border-[#1F293D] space-y-2">
                <span className="font-semibold text-gray-200">Linux Single-Line Command:</span>
                <pre className="p-3 rounded-lg bg-[#111827] border border-[#1F293D] font-mono text-[11px] text-cyan-400 whitespace-pre-wrap">
                  {linuxCurlCmd}
                </pre>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-[#1F293D]">
              <button
                onClick={() => setShowEnrollModal(false)}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition"
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
