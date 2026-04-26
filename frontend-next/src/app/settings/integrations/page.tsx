"use client";

import { useState } from "react";

const integrations = [
  { id: "aws", name: "Amazon Web Services", icon: "aws", connected: 3, status: "active" },
  { id: "azure", name: "Microsoft Azure", icon: "azure", connected: 2, status: "active" },
  { id: "gcp", name: "Google Cloud Platform", icon: "gcp", connected: 1, status: "active" },
  { id: "vmware", name: "VMware vCenter", icon: "vmware", connected: 1, status: "inactive" },
];

export default function SettingsIntegrationsPage() {
  const [showModal, setShowModal] = useState<string | null>(null);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-slide-down">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Settings</h1>
        <p className="text-gray-500 mt-1">Cloud account integrations</p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="col-span-1">
          <div className="bg-white rounded-2xl shadow-md p-4 animate-fade-in-up delay-100">
            <nav className="space-y-1">
              {[
                { label: "General", href: "/settings/general", active: false },
                { label: "Email", href: "/settings/email", active: false },
                { label: "Integrations", href: "/settings/integrations", active: true },
              ].map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${
                    item.active ? "bg-[#1E3A5F] text-white" : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {item.label}
                </a>
              ))}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="col-span-3 space-y-6">
          {/* Integration Cards */}
          <div className="grid grid-cols-2 gap-6">
            {integrations.map((integration, idx) => (
              <div key={integration.id} className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up" style={{ animationDelay: `${idx * 0.1}s` }}>
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#1E3A5F] to-[#0F2A4F] flex items-center justify-center">
                      <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" className="w-6 h-6">
                        <path d="M12 2L2 7l10 5 10-5-10-5z" />
                        <path d="M2 17l10 5 10-5" />
                        <path d="M2 12l10 5 10-5" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800">{integration.name}</h3>
                      <span className={`text-xs font-medium ${integration.status === "active" ? "text-emerald-600" : "text-gray-500"}`}>
                        {integration.status === "active" ? "Connected" : "Not Connected"}
                      </span>
                    </div>
                  </div>
                </div>
                
                {integration.status === "active" ? (
                  <>
                    <div className="text-sm text-gray-500 mb-4">{integration.connected} accounts connected</div>
                    <div className="flex gap-2">
                      <button className="flex-1 py-2 bg-[#1E3A5F] text-white rounded-xl text-sm font-medium hover:bg-[#0F2A4F] transition-colors">
                        Manage
                      </button>
                      <button className="px-4 py-2 border border-gray-200 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-50">
                        Test
                      </button>
                    </div>
                  </>
                ) : (
                  <button
                    onClick={() => setShowModal(integration.id)}
                    className="w-full py-2 border-2 border-dashed border-gray-200 rounded-xl text-sm font-medium text-gray-500 hover:border-[#1E3A5F] hover:text-[#1E3A5F] transition-colors"
                  >
                    Connect
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* API Keys */}
          <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-400">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">API Keys</h2>
              <button className="px-4 py-2 bg-[#1E3A5F] text-white rounded-xl text-sm font-medium hover:bg-[#0F2A4F] transition-colors">
                Generate New Key
              </button>
            </div>
            <div className="space-y-3">
              {[
                { name: "Production API Key", key: "cis_live_xxxx...xxxx4a2f", created: "2026-01-15", lastUsed: "2 hours ago" },
                { name: "Development API Key", key: "cis_test_xxxx...xxxx8b1c", created: "2026-02-20", lastUsed: "5 days ago" },
              ].map((apiKey, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
                  <div>
                    <div className="font-medium text-gray-800">{apiKey.name}</div>
                    <div className="text-sm text-gray-500 font-mono">{apiKey.key}</div>
                  </div>
                  <div className="text-right text-sm text-gray-500">
                    <div>Created: {apiKey.created}</div>
                    <div>Last used: {apiKey.lastUsed}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Connect Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-lg shadow-2xl animate-fade-in-up">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Connect {showModal.toUpperCase()}</h2>
              <button onClick={() => setShowModal(null)} className="p-2 hover:bg-gray-100 rounded-lg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Account ID / Subscription ID</label>
                <input type="text" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]" placeholder="Enter account ID" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Credentials</label>
                <textarea className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] h-24" placeholder="Paste JSON credentials or access key" />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowModal(null)} className="flex-1 py-3 border border-gray-200 rounded-xl font-semibold text-gray-600 hover:bg-gray-50">Cancel</button>
                <button type="submit" className="flex-1 py-3 bg-gradient-to-r from-[#1E3A5F] to-[#0F2A4F] text-white rounded-xl font-semibold">Connect</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}