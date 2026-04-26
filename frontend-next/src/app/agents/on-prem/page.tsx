"use client";

import { useState } from "react";

const agents = [
  { id: 1, hostname: "web-server-01", ip: "192.168.1.10", type: "Linux", os: "Ubuntu 22.04", status: "online", lastCheck: "2 min ago", findings: 3 },
  { id: 2, hostname: "db-server-01", ip: "192.168.1.11", type: "Linux", os: "RHEL 9.1", status: "online", lastCheck: "5 min ago", findings: 7 },
  { id: 3, hostname: "app-server-01", ip: "192.168.1.12", type: "Windows", os: "Windows Server 2022", status: "online", lastCheck: "1 min ago", findings: 2 },
  { id: 4, hostname: "fw-main-01", ip: "192.168.1.1", type: "Network", os: "FortiGate 600E", status: "online", lastCheck: "10 min ago", findings: 0 },
  { id: 5, hostname: "esxi-host-01", ip: "192.168.1.50", type: "VMware", os: "ESXi 8.0", status: "offline", lastCheck: "2 hours ago", findings: 12 },
  { id: 6, hostname: "k8s-node-01", ip: "192.168.2.10", type: "Kubernetes", os: "Ubuntu + K8s 1.28", status: "online", lastCheck: "3 min ago", findings: 1 },
];

export default function AgentsOnPremPage() {
  const [filter, setFilter] = useState("All");

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">On-Premise Agents</h1>
          <p className="text-gray-500 mt-1">Manage deployed scanning agents</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#1E3A5F] to-[#0F2A4F] text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Deploy Agent
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: "Total Agents", value: "6", color: "text-blue-500" },
          { label: "Online", value: "5", color: "text-emerald-500" },
          { label: "Offline", value: "1", color: "text-red-500" },
          { label: "Total Findings", value: "25", color: "text-amber-500" },
        ].map((stat, idx) => (
          <div key={idx} className={`bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-${idx + 1}00`}>
            <div className="text-sm font-medium text-gray-500">{stat.label}</div>
            <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 animate-fade-in-up delay-100">
        {["All", "Linux (2)", "Windows (1)", "Network (1)", "VMware (1)", "Kubernetes (1)"].map((f) => (
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

      {/* Agents Table */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden animate-fade-in-up delay-200">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Agent</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Type</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">OS</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Last Check</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Findings</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase"></th>
            </tr>
          </thead>
          <tbody>
            {agents.map((agent) => (
              <tr key={agent.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                      agent.type === "Linux" ? "bg-amber-100" :
                      agent.type === "Windows" ? "bg-blue-100" :
                      agent.type === "Network" ? "bg-purple-100" :
                      agent.type === "VMware" ? "bg-gray-100" : "bg-emerald-100"
                    }`}>
                      {agent.type === "Linux" && <svg viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2" className="w-5 h-5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>}
                      {agent.type === "Windows" && <svg viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2" className="w-5 h-5"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2z"/><path d="M12 12h8"/></svg>}
                      {agent.type === "Network" && <svg viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" strokeWidth="2" className="w-5 h-5"><circle cx="12" cy="12" r="2"/><path d="M12 2v4"/><path d="M12 18v4"/><path d="M4.93 4.93l2.83 2.83"/><path d="M16.24 16.24l2.83 2.83"/><path d="M2 12h4"/><path d="M18 12h4"/></svg>}
                      {agent.type === "VMware" && <svg viewBox="0 0 24 24" fill="none" stroke="#6B7280" strokeWidth="2" className="w-5 h-5"><rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/></svg>}
                      {agent.type === "Kubernetes" && <svg viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2" className="w-5 h-5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{agent.hostname}</div>
                      <div className="text-xs text-gray-500">{agent.ip}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-gray-600">{agent.type}</td>
                <td className="px-6 py-4 text-gray-600">{agent.os}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                    agent.status === "online" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                  }`}>
                    <span className={`w-2 h-2 rounded-full ${agent.status === "online" ? "bg-emerald-500" : "bg-red-500"} ${agent.status === "online" ? "animate-pulse" : ""}`} />
                    {agent.status === "online" ? "Online" : "Offline"}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-600">{agent.lastCheck}</td>
                <td className="px-6 py-4">
                  <span className={`font-semibold ${agent.findings > 5 ? "text-red-500" : agent.findings > 0 ? "text-amber-500" : "text-emerald-500"}`}>
                    {agent.findings}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="p-2 hover:bg-gray-100 rounded-lg">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-gray-400">
                      <circle cx="12" cy="12" r="1" /><circle cx="19" cy="12" r="1" /><circle cx="5" cy="12" r="1" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}