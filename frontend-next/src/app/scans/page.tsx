"use client";

import { useState } from "react";

const scans = [
  { id: 1, customer: "Acme Corp", type: "AWS CIS", status: "Completed", duration: "12m", findings: 8, date: "2026-04-20 14:30" },
  { id: 2, customer: "Beta Inc", type: "Azure Benchmark", status: "Running", duration: "8m", findings: null, date: "2026-04-20 15:00" },
  { id: 3, customer: "GlobalTech", type: "GCP Security", status: "Completed", duration: "15m", findings: 3, date: "2026-04-19 10:00" },
  { id: 4, customer: "HealthFirst", type: "Linux CIS", status: "Completed", duration: "25m", findings: 15, date: "2026-04-18 09:15" },
  { id: 5, customer: "FinServe Ltd", type: "Windows CIS", status: "Failed", duration: "5m", findings: null, date: "2026-04-17 16:45" },
];

export default function ScansPage() {
  const [showSchedule, setShowSchedule] = useState(false);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Scans</h1>
          <p className="text-gray-500 mt-1">Scan history and scheduling</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSchedule(true)}
            className="flex items-center gap-2 px-5 py-3 border border-gray-200 bg-white rounded-2xl font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            Schedule Scan
          </button>
          <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-2xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5 transition-all duration-300">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            Run Scan Now
          </button>
        </div>
      </div>

      {/* Scan History */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden animate-fade-in-up delay-200">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-bold">Scan History</h2>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Customer</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Type</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Duration</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Findings</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase">Date</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase"></th>
            </tr>
          </thead>
          <tbody>
            {scans.map((scan) => (
              <tr key={scan.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-6 py-4 font-semibold text-gray-800">{scan.customer}</td>
                <td className="px-6 py-4 text-gray-600">{scan.type}</td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                    scan.status === "Completed" ? "bg-emerald-100 text-emerald-700" :
                    scan.status === "Running" ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-700"
                  }`}>
                    {scan.status === "Running" && <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />}
                    {scan.status === "Completed" && <span className="w-2 h-2 bg-emerald-500 rounded-full" />}
                    {scan.status === "Failed" && <span className="w-2 h-2 bg-red-500 rounded-full" />}
                    {scan.status}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-600">{scan.duration}</td>
                <td className="px-6 py-4">
                  {scan.findings !== null ? (
                    <span className={`font-semibold ${scan.findings > 10 ? "text-red-500" : scan.findings > 5 ? "text-amber-500" : "text-emerald-500"}`}>
                      {scan.findings}
                    </span>
                  ) : <span className="text-gray-400">-</span>}
                </td>
                <td className="px-6 py-4 text-gray-600">{scan.date}</td>
                <td className="px-6 py-4">
                  {scan.status === "Completed" && (
                    <button className="text-[#1E3A5F] font-medium text-sm hover:underline">View Results</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Schedule Modal */}
      {showSchedule && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 w-full max-w-lg shadow-2xl animate-fade-in-up">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Schedule Scan</h2>
              <button onClick={() => setShowSchedule(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Customer</label>
                <select className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]">
                  <option>Acme Corp</option>
                  <option>Beta Inc</option>
                  <option>GlobalTech</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Scan Type</label>
                <select className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]">
                  <option>AWS CIS Benchmark</option>
                  <option>Azure Security Benchmark</option>
                  <option>GCP Security Benchmark</option>
                  <option>Linux CIS Benchmark</option>
                  <option>Windows CIS Benchmark</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Frequency</label>
                <select className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]">
                  <option>Daily</option>
                  <option>Weekly</option>
                  <option>Monthly</option>
                </select>
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowSchedule(false)} className="flex-1 py-3 border border-gray-200 rounded-xl font-semibold text-gray-600 hover:bg-gray-50">Cancel</button>
                <button type="submit" className="flex-1 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl font-semibold">Schedule</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}