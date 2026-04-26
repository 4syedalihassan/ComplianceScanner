"use client";

import { useState, useEffect } from "react";

const benchmarks = [
  { name: "CIS AWS Foundations Benchmark", version: "3.0", controls: 241, compliant: 198, nonCompliant: 28, notApplicable: 15, score: 88 },
  { name: "CIS Microsoft Azure Foundations Benchmark", version: "3.0", controls: 185, compliant: 156, nonCompliant: 18, notApplicable: 11, score: 90 },
  { name: "CIS Google Cloud Platform Foundation Benchmark", version: "3.0", controls: 162, compliant: 134, nonCompliant: 16, notApplicable: 12, score: 89 },
  { name: "CIS Linux Enterprise Benchmark", version: "9.2", controls: 287, compliant: 245, nonCompliant: 32, notApplicable: 10, score: 88 },
  { name: "CIS Windows Server 2022 Benchmark", version: "1.0", controls: 186, compliant: 152, nonCompliant: 22, notApplicable: 12, score: 87 },
  { name: "CIS Kubernetes Benchmark", version: "1.7", controls: 114, compliant: 98, nonCompliant: 10, notApplicable: 6, score: 91 },
];

export default function CompliancePage() {
  const [selectedBenchmark, setSelectedBenchmark] = useState(benchmarks[0]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-slide-down">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Compliance</h1>
        <p className="text-gray-500 mt-1">CIS Benchmark compliance status across all environments</p>
      </div>

      {/* Overall Score */}
      <div className="grid grid-cols-4 gap-6">
        <div className="col-span-1 bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-100">
          <div className="text-sm font-medium text-gray-500 mb-2">Overall Compliance</div>
          <div className="text-5xl font-extrabold text-emerald-500">89%</div>
          <div className="mt-4 h-3 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full" style={{ width: "89%" }} />
          </div>
        </div>
        <div className="col-span-3 grid grid-cols-3 gap-4">
          <div className="bg-white rounded-2xl p-5 shadow-md animate-fade-in-up delay-200">
            <div className="text-sm font-medium text-gray-500">Total Controls</div>
            <div className="text-3xl font-bold text-gray-800">1,175</div>
          </div>
          <div className="bg-white rounded-2xl p-5 shadow-md animate-fade-in-up delay-300">
            <div className="text-sm font-medium text-gray-500">Compliant</div>
            <div className="text-3xl font-bold text-emerald-500">983</div>
          </div>
          <div className="bg-white rounded-2xl p-5 shadow-md animate-fade-in-up delay-400">
            <div className="text-sm font-medium text-gray-500">Non-Compliant</div>
            <div className="text-3xl font-bold text-red-500">126</div>
          </div>
        </div>
      </div>

      {/* Benchmark List */}
      <div className="bg-white rounded-2xl shadow-md overflow-hidden animate-fade-in-up delay-500">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-bold">Benchmark Details</h2>
        </div>
        <div className="divide-y divide-gray-100">
          {benchmarks.map((benchmark, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedBenchmark(benchmark)}
              className={`p-6 cursor-pointer hover:bg-gray-50 transition-colors ${selectedBenchmark.name === benchmark.name ? "bg-blue-50/50" : ""}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-bold text-gray-800">{benchmark.name}</h3>
                    <span className="px-2 py-0.5 bg-gray-100 rounded text-xs text-gray-600">v{benchmark.version}</span>
                  </div>
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span>{benchmark.controls} controls</span>
                    <span className="text-emerald-600">{benchmark.compliant} compliant</span>
                    <span className="text-red-600">{benchmark.nonCompliant} failed</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-3xl font-extrabold ${benchmark.score >= 90 ? "text-emerald-500" : benchmark.score >= 80 ? "text-amber-500" : "text-red-500"}`}>
                    {benchmark.score}%
                  </div>
                  <div className="text-xs text-gray-500">Compliance</div>
                </div>
              </div>
              <div className="mt-4 h-2 bg-gray-100 rounded-full overflow-hidden flex">
                <div className="bg-emerald-500" style={{ width: `${(benchmark.compliant / benchmark.controls) * 100}%` }} />
                <div className="bg-red-500" style={{ width: `${(benchmark.nonCompliant / benchmark.controls) * 100}%` }} />
                <div className="bg-gray-300 flex-1" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Selected Benchmark Details */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-600">
          <h3 className="font-bold text-gray-800 mb-4">Compliant Controls</h3>
          <div className="space-y-3">
            {[
              "1.1.1 - Ensure credentials satisfy complexity requirements",
              "1.2.2 - Ensure password reuse is limited",
              "2.1.1 - Ensure CloudTrail is enabled in all regions",
              "3.1.1 - Ensure VPC Flow Logs is enabled",
              "4.1.1 - Ensure S3 bucket policy denies unencrypted uploads",
            ].map((control, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-emerald-50 rounded-xl">
                <svg viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2" className="w-5 h-5 flex-shrink-0">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span className="text-sm text-gray-700">{control}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-600">
          <h3 className="font-bold text-gray-800 mb-4">Non-Compliant Controls</h3>
          <div className="space-y-3">
            {[
              "1.1.2 - Ensure MFA for root account",
              "2.3.1 - Ensure CloudTrail log file validation is enabled",
              "4.2.1 - Ensure S3 buckets are encrypted",
              "5.1.1 - Ensure security groups restrict unauthorized access",
            ].map((control, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-red-50 rounded-xl">
                <svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" className="w-5 h-5 flex-shrink-0">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="15" y1="9" x2="9" y2="15" />
                  <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
                <span className="text-sm text-gray-700">{control}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}