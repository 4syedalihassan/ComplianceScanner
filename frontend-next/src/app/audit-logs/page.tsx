"use client";

import { useState } from "react";

const auditLogs = [
  { id: 1, action: "USER_LOGIN", user: "admin@company.com", ip: "192.168.1.100", details: "Successful login with MFA", timestamp: "2026-04-20 14:30:45" },
  { id: 2, action: "SCAN_COMPLETED", user: "john@company.com", ip: "192.168.1.101", details: "AWS CIS scan completed - 8 findings", timestamp: "2026-04-20 14:25:12" },
  { id: 3, action: "CUSTOMER_CREATED", user: "admin@company.com", ip: "192.168.1.100", details: "New customer added: TechCorp", timestamp: "2026-04-20 13:15:33" },
  { id: 4, action: "REPORT_GENERATED", user: "sarah@company.com", ip: "192.168.1.102", details: "Generated Q1 2026 report for Acme Corp", timestamp: "2026-04-20 12:00:00" },
  { id: 5, action: "USER_MFA_ENABLED", user: "lisa@company.com", ip: "192.168.1.103", details: "MFA enabled via TOTP", timestamp: "2026-04-20 11:45:22" },
  { id: 6, action: "FAILED_LOGIN", user: "unknown", ip: "10.0.0.55", details: "Failed login attempt - invalid password", timestamp: "2026-04-20 10:30:11" },
  { id: 7, action: "SETTINGS_UPDATED", user: "admin@company.com", ip: "192.168.1.100", details: "Email notification settings updated", timestamp: "2026-04-20 09:20:45" },
  { id: 8, action: "SCAN_SCHEDULED", user: "john@company.com", ip: "192.168.1.101", details: "Weekly scan scheduled for Acme Corp", timestamp: "2026-04-19 16:00:00" },
];

const actionColors: Record<string, string> = {
  USER_LOGIN: "bg-emerald-100 text-emerald-700",
  SCAN_COMPLETED: "bg-blue-100 text-blue-700",
  CUSTOMER_CREATED: "bg-purple-100 text-purple-700",
  REPORT_GENERATED: "bg-amber-100 text-amber-700",
  USER_MFA_ENABLED: "bg-teal-100 text-teal-700",
  FAILED_LOGIN: "bg-red-100 text-red-700",
  SETTINGS_UPDATED: "bg-indigo-100 text-indigo-700",
  SCAN_SCHEDULED: "bg-cyan-100 text-cyan-700",
};

export default function AuditLogsPage() {
  const [filter, setFilter] = useState("All");

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Audit Logs</h1>
          <p className="text-gray-500 mt-1">System audit trail and activity history</p>
        </div>
        <button className="flex items-center gap-2 px-5 py-3 border border-gray-200 bg-white rounded-2xl font-semibold text-gray-700 hover:bg-gray-50 transition-colors">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Export Logs
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 animate-fade-in-up delay-100">
        {["All", "Authentication", "Scans", "Users", "Settings"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              filter === f ? "bg-[#1E3A5F] text-white" : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Logs Table */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden animate-fade-in-up delay-200">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Timestamp</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Action</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">User</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">IP Address</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Details</th>
            </tr>
          </thead>
          <tbody>
            {auditLogs.map((log) => (
              <tr key={log.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">{log.timestamp}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${actionColors[log.action] || "bg-gray-100 text-gray-700"}`}>
                    {log.action.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="font-medium text-gray-800">{log.user}</span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-600 font-mono">{log.ip}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{log.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}