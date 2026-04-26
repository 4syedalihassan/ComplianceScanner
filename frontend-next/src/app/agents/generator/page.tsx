"use client";

import { useState } from "react";

export default function AgentGeneratorPage() {
  const [osType, setOsType] = useState("linux");
  const [customer, setCustomer] = useState("acme");
  const [generatedScript, setGeneratedScript] = useState("");

  const generateScript = () => {
    const scripts: Record<string, string> = {
      linux: `#!/bin/bash
# CIS Compliance Agent - Linux
# Customer: ${customer}
# Generated: ${new Date().toISOString()}

set -e

echo "Installing CIS Compliance Agent..."

# Download agent
curl -fsSL https://agents.compliance-scanner.io/install.sh | bash

# Configure agent
cat > /etc/cis-agent/config.yaml << EOF
customer_id: "${customer}"
agent_type: "linux"
api_endpoint: "https://api.compliance-scanner.io"
api_key: "\${CIS_API_KEY}"
scan_interval: "24h"
EOF

# Start agent
systemctl enable cis-agent
systemctl start cis-agent

echo "Agent installed successfully!"`,
      
      windows: `@echo off
REM CIS Compliance Agent - Windows
REM Customer: ${customer}
REM Generated: ${new Date().toISOString()}

echo Installing CIS Compliance Agent...

REM Download and install agent
powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest -Uri 'https://agents.compliance-scanner.io/cis-agent.exe' -OutFile 'C:\\Program Files\\CIS Agent\\cis-agent.exe'"

REM Configure agent
echo customer_id: ${customer} > "C:\\Program Files\\CIS Agent\\config.yaml"
echo agent_type: windows >> "C:\\Program Files\\CIS Agent\\config.yaml"
echo api_endpoint: https://api.compliance-scanner.io >> "C:\\Program Files\\CIS Agent\\config.yaml"

REM Install as service
sc create "CIS-Agent" binPath= "C:\\Program Files\\CIS Agent\\cis-agent.exe" start= auto
sc start "CIS-Agent"

echo Agent installed successfully!
pause`,
      
      docker: `# CIS Compliance Agent - Docker
# Customer: ${customer}
# Generated: ${new Date().toISOString()}

version: '3.8'

services:
  cis-agent:
    image: compliance-scanner/agent:latest
    container_name: cis-agent-${customer}
    environment:
      - CUSTOMER_ID=${customer}
      - API_ENDPOINT=https://api.compliance-scanner.io
      - API_KEY=\${CIS_API_KEY}
      - AGENT_TYPE=docker
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /etc:/etc:ro
    restart: unless-stopped

# Run with:
# docker-compose up -d`,
      
      kubernetes: `# CIS Compliance Agent - Kubernetes
# Customer: ${customer}
# Generated: ${new Date().toISOString()}

apiVersion: v1
kind: ServiceAccount
metadata:
  name: cis-agent
  namespace: cis-compliance
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cis-agent
subjects:
- kind: ServiceAccount
  name: cis-agent
  namespace: cis-compliance
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: cis-agent
  namespace: cis-compliance
spec:
  selector:
    matchLabels:
      app: cis-agent
  template:
    metadata:
      labels:
        app: cis-agent
    spec:
      serviceAccountName: cis-agent
      containers:
      - name: agent
        image: compliance-scanner/k8s-agent:latest
        env:
        - name: CUSTOMER_ID
          value: "${customer}"
        - name: API_ENDPOINT
          value: "https://api.compliance-scanner.io"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: cis-agent-secrets
              key: api-key
        securityContext:
          privileged: true
        volumeMounts:
        - name: etc
          mountPath: /etc
          readOnly: true
      volumes:
      - name: etc
        hostPath:
          path: /etc`,
    };

    setGeneratedScript(scripts[osType]);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(generatedScript);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Agent Generator</h1>
          <p className="text-gray-500 mt-1">Generate installation scripts for on-premise agents</p>
        </div>
      </div>

      {/* Configuration */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 space-y-6">
          <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-100">
            <h2 className="text-lg font-bold mb-4">Agent Configuration</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Customer</label>
                <select 
                  value={customer} 
                  onChange={(e) => setCustomer(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]"
                >
                  <option value="acme">Acme Corp</option>
                  <option value="beta">Beta Inc</option>
                  <option value="globaltech">GlobalTech</option>
                  <option value="healthfirst">HealthFirst</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Target OS</label>
                <select 
                  value={osType} 
                  onChange={(e) => setOsType(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]"
                >
                  <option value="linux">Linux (Bash)</option>
                  <option value="windows">Windows (PowerShell)</option>
                  <option value="docker">Docker</option>
                  <option value="kubernetes">Kubernetes</option>
                </select>
              </div>
            </div>
            <div className="mt-6">
              <button
                onClick={generateScript}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-2xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5 transition-all duration-300"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <path d="M12 2v10" />
                  <path d="M18.5 8a6.5 6.5 0 1 1-13 0" />
                </svg>
                Generate Script
              </button>
            </div>
          </div>

          {/* Generated Script */}
          {generatedScript && (
            <div className="bg-[#1a1a2e] rounded-2xl p-6 shadow-md animate-fade-in-up delay-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-white">Generated Script</h2>
                <div className="flex gap-2">
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-xl text-sm font-medium hover:bg-white/20 transition-colors"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <rect x="9" y="9" width="13" height="13" rx="2" />
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                    </svg>
                    Copy
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-xl text-sm font-medium hover:bg-white/20 transition-colors">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    Download
                  </button>
                </div>
              </div>
              <pre className="text-gray-300 text-sm font-mono overflow-x-auto whitespace-pre-wrap max-h-96">
                {generatedScript}
              </pre>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-300">
            <h3 className="font-bold text-gray-800 mb-4">Quick Start</h3>
            <div className="space-y-4 text-sm">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-emerald-600 font-bold">1</span>
                </div>
                <div>
                  <div className="font-medium text-gray-800">Select Customer</div>
                  <div className="text-gray-500">Choose which customer to assign the agent to</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-emerald-600 font-bold">2</span>
                </div>
                <div>
                  <div className="font-medium text-gray-800">Choose OS</div>
                  <div className="text-gray-500">Select the target operating system</div>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-emerald-600 font-bold">3</span>
                </div>
                <div>
                  <div className="font-medium text-gray-800">Generate & Deploy</div>
                  <div className="text-gray-500">Copy the script and run on target</div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 rounded-2xl p-6 animate-fade-in-up delay-400">
            <div className="flex items-start gap-3">
              <svg viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2" className="w-6 h-6 flex-shrink-0">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
              <div>
                <div className="font-semibold text-blue-800">API Key Required</div>
                <p className="text-sm text-blue-600 mt-1">Make sure to set the CIS_API_KEY environment variable before running the script.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}