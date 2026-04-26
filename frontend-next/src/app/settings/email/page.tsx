"use client";

import { useState } from "react";

export default function SettingsEmailPage() {
  const [saved, setSaved] = useState(false);
  const [testSent, setTestSent] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleTestEmail = () => {
    setTestSent(true);
    setTimeout(() => setTestSent(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-slide-down">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Settings</h1>
        <p className="text-gray-500 mt-1">Email notification configuration</p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="col-span-1">
          <div className="bg-white rounded-2xl shadow-md p-4 animate-fade-in-up delay-100">
            <nav className="space-y-1">
              {[
                { label: "General", href: "/settings/general", active: false },
                { label: "Email", href: "/settings/email", active: true },
                { label: "Integrations", href: "/settings/integrations", active: false },
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
          {/* SMTP Configuration */}
          <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-200">
            <h2 className="text-lg font-bold mb-4">SMTP Configuration</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Host</label>
                <input type="text" defaultValue="smtp.gmail.com" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">SMTP Port</label>
                <input type="text" defaultValue="587" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Encryption</label>
                <select className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]">
                  <option>TLS</option>
                  <option>SSL</option>
                  <option>None</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                <input type="text" defaultValue="alerts@company.com" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                <input type="password" defaultValue="********" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]" />
              </div>
            </div>
            <div className="mt-4">
              <button
                onClick={handleTestEmail}
                className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl font-medium text-gray-600 hover:bg-gray-50 transition-colors"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                  <path d="M22 2L11 13" /><path d="M22 2l-7 20-4-9-9-4 20-7z" />
                </svg>
                {testSent ? "Test Email Sent!" : "Send Test Email"}
              </button>
            </div>
          </div>

          {/* Notification Triggers */}
          <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-300">
            <h2 className="text-lg font-bold mb-4">Notification Triggers</h2>
            <div className="space-y-4">
              {[
                { label: "Critical findings detected", description: "Notify when new critical severity findings are detected", enabled: true },
                { label: "Scan completed", description: "Notify when a scan finishes", enabled: true },
                { label: "Drift detected", description: "Notify when compliance drift is detected", enabled: true },
                { label: "Weekly summary", description: "Send weekly compliance summary report", enabled: false },
                { label: "Monthly report", description: "Send monthly executive report", enabled: true },
              ].map((trigger, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 border border-gray-200 rounded-xl">
                  <div>
                    <div className="font-medium text-gray-800">{trigger.label}</div>
                    <div className="text-sm text-gray-500">{trigger.description}</div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked={trigger.enabled} className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 rounded-full peer peer-checked:bg-emerald-500 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Recipients */}
          <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-400">
            <h2 className="text-lg font-bold mb-4">Email Recipients</h2>
            <div className="space-y-3">
              {["admin@company.com", "security@company.com", "compliance@company.com"].map((email, idx) => (
                <div key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-gray-400">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  <span className="flex-1 text-gray-700">{email}</span>
                  <button className="text-gray-400 hover:text-red-500 transition-colors">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                  </button>
                </div>
              ))}
              <button className="w-full p-3 border-2 border-dashed border-gray-200 rounded-xl text-gray-500 hover:border-[#1E3A5F] hover:text-[#1E3A5F] transition-colors flex items-center justify-center gap-2">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                  <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                Add Recipient
              </button>
            </div>
          </div>

          {/* Save */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#1E3A5F] to-[#0F2A4F] text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
            >
              {saved ? "Saved!" : "Save Changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}