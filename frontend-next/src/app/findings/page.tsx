"use client";

import { useState } from "react";

const findings = [
  { id: 1, control: "1.1.1", title: "Ensure mounting of cramfs filesystems is disabled", description: "The cramfs filesystem is still available on the system. This could be used to escalate privileges.", severity: "Critical", status: "Open", asset: "server-01", customer: "Acme Corp", scanDate: "2026-04-15" },
  { id: 2, control: "2.1", title: "Ensure CloudTrail is enabled", description: "CloudTrail is not enabled for this AWS account.", severity: "High", status: "Open", asset: "aws-account-123456", customer: "Beta Inc", scanDate: "2026-04-18" },
  { id: 3, control: "4.2", title: "Ensure S3 bucket policy is configured to deny unencrypted uploads", description: "Bucket does not have encryption policy enforced.", severity: "Medium", status: "Open", asset: "s3://data-bucket", customer: "Acme Corp", scanDate: "2026-04-15" },
  { id: 4, control: "3.5", title: "Ensure VPC Flow Logs is enabled", description: "VPC Flow Logs are not enabled for this VPC.", severity: "Medium", status: "Resolved", asset: "vpc-main", customer: "GlobalTech", scanDate: "2026-04-10" },
  { id: 5, control: "1.2.3", title: "Ensure authentication is enabled for the console", description: "Password authentication is not configured.", severity: "High", status: "Open", asset: "linux-host-05", customer: "HealthFirst", scanDate: "2026-04-19" },
];

const severityColors: Record<string, string> = {
  Critical: "bg-red-100 text-red-700",
  High: "bg-amber-100 text-amber-700",
  Medium: "bg-blue-100 text-blue-700",
  Low: "bg-emerald-100 text-emerald-700",
};

const severityBars: Record<string, string> = {
  Critical: "from-red-500 to-red-400",
  High: "from-amber-500 to-amber-400",
  Medium: "from-blue-500 to-blue-400",
  Low: "from-emerald-500 to-emerald-400",
};

export default function FindingsPage() {
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");

  const filters = ["All", "Critical (3)", "High (12)", "Medium (45)", "Low (67)"];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Findings</h1>
          <p className="text-gray-500 mt-1">Review and manage security findings across all environments</p>
        </div>
        <div className="relative">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder="Search findings..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-12 pr-4 py-3 w-80 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 animate-fade-in-up delay-100">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              filter === f
                ? "bg-[#1E3A5F] text-white"
                : "bg-white text-gray-600 hover:bg-gray-50 border border-gray-200"
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Findings List */}
      <div className="space-y-4">
        {findings.map((finding, idx) => (
          <div
            key={finding.id}
            className={`bg-white rounded-2xl p-6 shadow-md hover:shadow-xl transition-all duration-300 animate-fade-in-up`}
            style={{ animationDelay: `${idx * 0.1}s` }}
          >
            <div className="flex items-start gap-4">
              {/* Severity Bar */}
              <div className={`w-1 h-full rounded-full bg-gradient-to-b ${severityBars[finding.severity]}`} style={{ minHeight: "80px" }} />
              
              <div className="flex-1">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-sm font-semibold text-gray-500">{finding.control}</span>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${severityColors[finding.severity]}`}>
                        {finding.severity}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        finding.status === "Open" ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"
                      }`}>
                        {finding.status}
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-gray-800">{finding.title}</h3>
                  </div>
                  <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-gray-400">
                      <circle cx="12" cy="12" r="1" />
                      <circle cx="19" cy="12" r="1" />
                      <circle cx="5" cy="12" r="1" />
                    </svg>
                  </button>
                </div>
                <p className="text-gray-600 mb-4">{finding.description}</p>
                <div className="flex items-center gap-6 text-sm text-gray-500">
                  <span className="flex items-center gap-2">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <rect x="2" y="2" width="20" height="8" rx="2" />
                      <rect x="2" y="14" width="20" height="8" rx="2" />
                    </svg>
                    {finding.asset}
                  </span>
                  <span className="flex items-center gap-2">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                    </svg>
                    {finding.customer}
                  </span>
                  <span className="flex items-center gap-2">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <rect x="3" y="4" width="18" height="18" rx="2" />
                      <line x1="16" y1="2" x2="16" y2="6" />
                      <line x1="8" y1="2" x2="8" y2="6" />
                    </svg>
                    {finding.scanDate}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}