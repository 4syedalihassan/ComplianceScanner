"use client";

import { useState, useEffect } from "react";

export default function LiveScanPage() {
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState("");
  const [logs, setLogs] = useState<string[]>([]);

  const steps = [
    "Initializing scan engine...",
    "Connecting to AWS API...",
    "Fetching IAM configuration...",
    "Checking S3 bucket policies...",
    "Validating CloudTrail settings...",
    "Analyzing VPC configurations...",
    "Checking security groups...",
    "Evaluating IAM policies...",
    "Scanning RDS instances...",
    "Generating report...",
  ];

  const startScan = () => {
    setScanning(true);
    setProgress(0);
    setLogs(["[START] Starting CIS AWS Benchmark scan..."]);
    let stepIndex = 0;

    const interval = setInterval(() => {
      if (stepIndex >= steps.length) {
        clearInterval(interval);
        setScanning(false);
        setLogs(prev => [...prev, "[COMPLETE] Scan finished successfully", `[RESULT] Found 8 findings (2 Critical, 3 High, 3 Medium)`]);
        return;
      }

      setCurrentStep(steps[stepIndex]);
      setProgress(((stepIndex + 1) / steps.length) * 100);
      setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${steps[stepIndex]}`]);
      stepIndex++;
    }, 1500);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Live Scan</h1>
          <p className="text-gray-500 mt-1">Execute real-time compliance scans</p>
        </div>
        <button
          onClick={startScan}
          disabled={scanning}
          className={`flex items-center gap-2 px-6 py-3 rounded-2xl font-semibold shadow-lg transition-all duration-300 ${
            scanning
              ? "bg-gray-100 text-gray-400 cursor-not-allowed"
              : "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white hover:shadow-emerald-500/40 hover:-translate-y-0.5"
          }`}
        >
          {scanning ? (
            <>
              <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Scanning...
            </>
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              Start Scan
            </>
          )}
        </button>
      </div>

      {/* Scan Configuration */}
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-100">
          <h2 className="text-lg font-bold mb-4">Target Configuration</h2>
          <div className="space-y-4">
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
              <label className="block text-sm font-medium text-gray-700 mb-2">Scan Scope</label>
              <div className="space-y-2">
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-xl cursor-pointer hover:bg-gray-50">
                  <input type="radio" name="scope" defaultChecked className="w-4 h-4 text-[#1E3A5F]" />
                  <span className="text-gray-700">Full Scan (All regions)</span>
                </label>
                <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-xl cursor-pointer hover:bg-gray-50">
                  <input type="radio" name="scope" className="w-4 h-4 text-[#1E3A5F]" />
                  <span className="text-gray-700">Single Region</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Card */}
        <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-200">
          <h2 className="text-lg font-bold mb-4">Scan Progress</h2>
          <div className="relative pt-8">
            <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="flex justify-between mt-2 text-sm text-gray-500">
              <span>0%</span>
              <span>{Math.round(progress)}%</span>
              <span>100%</span>
            </div>
          </div>
          
          {scanning && (
            <div className="mt-6 p-4 bg-blue-50 rounded-xl">
              <div className="flex items-center gap-2 text-blue-700 font-medium">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8" />
                </svg>
                {currentStep}
              </div>
            </div>
          )}

          {!scanning && progress === 0 && (
            <div className="mt-6 p-4 bg-gray-50 rounded-xl text-center text-gray-500">
              Ready to start scan
            </div>
          )}

          {progress === 100 && !scanning && (
            <div className="mt-6 p-4 bg-emerald-50 rounded-xl">
              <div className="flex items-center gap-2 text-emerald-700 font-medium">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Scan completed successfully
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Live Logs */}
      <div className="bg-[#1a1a2e] rounded-2xl p-6 shadow-md animate-fade-in-up delay-300">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">Live Logs</h2>
          <button
            onClick={() => setLogs([])}
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Clear
          </button>
        </div>
        <div className="h-64 overflow-y-auto font-mono text-sm space-y-1">
          {logs.length === 0 ? (
            <div className="text-gray-500">No logs yet. Start a scan to see output.</div>
          ) : (
            logs.map((log, idx) => (
              <div key={idx} className={`${
                log.includes("COMPLETE") ? "text-emerald-400" :
                log.includes("ERROR") ? "text-red-400" :
                log.includes("RESULT") ? "text-amber-400" :
                "text-gray-300"
              }`}>
                {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}