"use client";

import { useState } from "react";

const customers = [
  { id: 1, name: "Acme Corp", type: "Enterprise", env: "AWS + On-Prem", accounts: "3 AWS, 12 Linux", lastScan: "2 hours ago", score: 92, status: "Active", color: "from-blue-600 to-blue-500" },
  { id: 2, name: "Beta Inc", type: "SMB", env: "Azure", accounts: "2 Azure", lastScan: "1 day ago", score: 78, status: "Issues", color: "from-indigo-500 to-indigo-400" },
  { id: 3, name: "GlobalTech", type: "Enterprise", env: "GCP + K8s", accounts: "5 GKE, 2 GCS", lastScan: "3 days ago", score: 95, status: "Active", color: "from-amber-500 to-amber-400" },
  { id: 4, name: "FinServe Ltd", type: "Enterprise", env: "AWS + Azure", accounts: "4 AWS, 2 Azure", lastScan: "5 hours ago", score: 88, status: "Active", color: "from-pink-500 to-pink-400" },
  { id: 5, name: "HealthFirst", type: "Enterprise", env: "On-Prem", accounts: "45 Linux, 12 Win", lastScan: "1 day ago", score: 62, status: "Critical", color: "from-teal-500 to-teal-400" },
];

export default function CustomersPage() {
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Customers</h1>
          <p className="text-gray-500 mt-1">Manage your customer environments and scan targets</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#1E3A5F] to-[#0F2A4F] text-white rounded-2xl font-semibold shadow-lg shadow-[#1E3A5F]/25 hover:shadow-[#1E3A5F]/40 hover:-translate-y-0.5 transition-all duration-300"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Customer
        </button>
      </div>

      {/* Customers Table */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden animate-fade-in-up delay-200">
        <div className="p-6 border-b border-gray-100 flex justify-between items-center">
          <h2 className="text-lg font-bold">All Customers</h2>
          <span className="text-sm text-gray-500">{customers.length} customers</span>
        </div>
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Customer</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Environment</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Assets</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Last Scan</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Score</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"></th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${customer.color} flex items-center justify-center text-white font-bold shadow-md`}>
                      {customer.name[0]}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-800">{customer.name}</div>
                      <div className="text-xs text-gray-500">{customer.type}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-600">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <path d="M12 2L2 7l10 5 10-5-10-5z" />
                      <path d="M2 17l10 5 10-5" />
                      <path d="M2 12l10 5 10-5" />
                    </svg>
                    {customer.env}
                  </span>
                </td>
                <td className="px-6 py-4 text-gray-600">{customer.accounts}</td>
                <td className="px-6 py-4 text-gray-600">{customer.lastScan}</td>
                <td className="px-6 py-4">
                  <span className={`font-bold text-lg ${customer.score >= 90 ? "text-emerald-500" : customer.score >= 70 ? "text-amber-500" : "text-red-500"}`}>
                    {customer.score}%
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                    customer.status === "Active" ? "bg-emerald-100 text-emerald-700" :
                    customer.status === "Issues" ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-700"
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      customer.status === "Active" ? "bg-emerald-500" :
                      customer.status === "Issues" ? "bg-amber-500" : "bg-red-500"
                    }`} />
                    {customer.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-gray-400">
                      <circle cx="12" cy="12" r="1" />
                      <circle cx="19" cy="12" r="1" />
                      <circle cx="5" cy="12" r="1" />
                    </svg>
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Customer Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fade-in-up">
          <div className="bg-white rounded-2xl p-8 w-full max-w-lg shadow-2xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Add New Customer</h2>
              <button onClick={() => setShowModal(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                <input type="text" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent" placeholder="Acme Corporation" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Environment Type</label>
                <select className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent">
                  <option>AWS</option>
                  <option>Azure</option>
                  <option>GCP</option>
                  <option>On-Premise</option>
                  <option>Multi-Cloud</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Account ID / Credentials</label>
                <input type="text" className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent" placeholder="AWS Account ID or connection string" />
              </div>
              <div className="flex gap-3 pt-4">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 py-3 border border-gray-200 rounded-xl font-semibold text-gray-600 hover:bg-gray-50 transition-colors">Cancel</button>
                <button type="submit" className="flex-1 py-3 bg-gradient-to-r from-[#1E3A5F] to-[#0F2A4F] text-white rounded-xl font-semibold hover:shadow-lg transition-all">Add Customer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}