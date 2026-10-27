import React, { useState } from 'react';
import { Shield, Lock, Mail, AlertCircle, ArrowRight, Loader2, KeyRound } from 'lucide-react';
import { loginUser, AuthUser } from '../api/auth';

interface LoginProps {
  onLoginSuccess: (user: AuthUser) => void;
}

export const LoginPage: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('admin@fim.local');
  const [password, setPassword] = useState('Admin@FIM2026!Secure');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const result = await loginUser(email, password);
    setLoading(false);

    if (result.success && result.user) {
      onLoginSuccess(result.user);
    } else {
      setError(result.error || 'Authentication failed');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#0B0F17] p-6 relative overflow-hidden select-none">
      {/* Background ambient glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md relative z-10">
        
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-blue-600 flex items-center justify-center text-white shadow-xl shadow-blue-600/30 mb-4 border border-blue-400/20">
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">FIM Enterprise</h1>
          <p className="text-xs text-gray-400 mt-1">Windows & Linux File Integrity Monitoring</p>
        </div>

        {/* Login Card */}
        <div className="glass-panel rounded-2xl p-8 border border-[#1F293D] shadow-2xl">
          <h2 className="text-base font-semibold text-white mb-1">Sign In to Console</h2>
          <p className="text-xs text-gray-400 mb-6">Enter administrative or analyst credentials</p>

          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-950/60 border border-rose-800/60 text-rose-300 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1.5">Work Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@fim.local"
                  className="w-full bg-[#0B0F17] border border-[#1F293D] rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-gray-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-[#0B0F17] border border-[#1F293D] rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-600/30 transition disabled:opacity-50 mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span>Authenticate & Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick RBAC Role Selectors */}
          <div className="mt-6 pt-5 border-t border-[#1F293D] space-y-3">
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span className="flex items-center gap-1.5 font-medium text-gray-300">
                <KeyRound className="w-3.5 h-3.5 text-blue-400" /> Select Demo Role (RBAC)
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => {
                  setEmail('admin@fim.local');
                  setPassword('Admin@FIM2026!Secure');
                }}
                className={`p-2.5 rounded-xl border text-left transition flex flex-col justify-between ${
                  email === 'admin@fim.local'
                    ? 'bg-blue-950/60 border-blue-500/80 text-white'
                    : 'bg-[#0B0F17] border-[#1F293D] text-gray-300 hover:border-gray-600'
                }`}
              >
                <div className="font-semibold text-xs text-blue-400">Admin</div>
                <div className="text-[10px] text-gray-400 mt-1">Full Control</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setEmail('analyst@fim.local');
                  setPassword('Analyst@FIM2026!Secure');
                }}
                className={`p-2.5 rounded-xl border text-left transition flex flex-col justify-between ${
                  email === 'analyst@fim.local'
                    ? 'bg-cyan-950/60 border-cyan-500/80 text-white'
                    : 'bg-[#0B0F17] border-[#1F293D] text-gray-300 hover:border-gray-600'
                }`}
              >
                <div className="font-semibold text-xs text-cyan-400">Analyst</div>
                <div className="text-[10px] text-gray-400 mt-1">Events & Alerts</div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setEmail('auditor@fim.local');
                  setPassword('Auditor@FIM2026!Secure');
                }}
                className={`p-2.5 rounded-xl border text-left transition flex flex-col justify-between ${
                  email === 'auditor@fim.local'
                    ? 'bg-emerald-950/60 border-emerald-500/80 text-white'
                    : 'bg-[#0B0F17] border-[#1F293D] text-gray-300 hover:border-gray-600'
                }`}
              >
                <div className="font-semibold text-xs text-emerald-400">Auditor</div>
                <div className="text-[10px] text-gray-400 mt-1">Read-Only Audit</div>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-[11px] text-gray-400 mt-6 font-mono">
          Argon2id Hashing • Role-Based Access Control (RBAC) • JWT Auth
        </p>
      </div>
    </div>
  );
};
