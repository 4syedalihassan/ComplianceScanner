import Link from "next/link";

export default function DashboardPage() {
  const stats = [
    { label: "Compliance Score", value: "87%", color: "success", icon: "chart", delay: "delay-100" },
    { label: "Total Customers", value: "12", color: "info", icon: "building", delay: "delay-200" },
    { label: "Critical Findings", value: "3", color: "danger", icon: "alert", delay: "delay-300" },
    { label: "Active Scans", value: "2", color: "warning", icon: "scan", delay: "delay-400" },
  ];

  const recentFindings = [
    { control: "1.1.1", title: "Ensure password policy enabled", severity: "High", status: "Fail", severityColor: "danger" },
    { control: "2.1", title: "Ensure CloudTrail is enabled", severity: "Low", status: "Pass", severityColor: "success" },
    { control: "4.1", title: "Ensure S3 encryption at rest", severity: "Medium", status: "Fail", severityColor: "warning" },
    { control: "5.2", title: "Ensure MFA for root account", severity: "Low", status: "Pass", severityColor: "success" },
    { control: "3.1", title: "Ensure Network Firewall enabled", severity: "Low", status: "Pass", severityColor: "success" },
  ];

  const activities = [
    { type: "success", title: "Scan completed for Acme Corp", desc: "AWS CIS Benchmark - 127 controls checked", time: "2 hours ago" },
    { type: "danger", title: "Critical finding detected", desc: "Root account MFA not enabled - AWS", time: "3 hours ago" },
    { type: "info", title: "Report generated", desc: "Q1 2026 Compliance Report - Acme Corp", time: "1 day ago" },
  ];

  const severityData = [
    { label: "Critical", count: 3, width: "15%", color: "from-red-500 to-red-400" },
    { label: "High", count: 5, width: "25%", color: "from-amber-500 to-amber-400" },
    { label: "Medium", count: 8, width: "40%", color: "from-blue-500 to-blue-400" },
    { label: "Low", count: 4, width: "20%", color: "from-emerald-500 to-emerald-400" },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome back! Here is your compliance overview.</p>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/live-scan"
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-2xl font-semibold shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 hover:-translate-y-0.5 transition-all duration-300"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
              <polygon points="5 3 19 12 5 21 5 3" />
            </svg>
            Run Scan
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <div
            key={stat.label}
            className={`bg-white rounded-2xl p-6 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300 animate-fade-in-up ${stat.delay}`}
          >
            <div
              className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${
                stat.color === "success"
                  ? "bg-emerald-100"
                  : stat.color === "danger"
                  ? "bg-red-100"
                  : stat.color === "warning"
                  ? "bg-amber-100"
                  : "bg-blue-100"
              }`}
            >
              {stat.icon === "chart" && (
                <svg viewBox="0 0 24 24" fill="none" stroke={stat.color === "success" ? "#10B981" : stat.color === "danger" ? "#EF4444" : stat.color === "warning" ? "#F59E0B" : "#3B82F6"} strokeWidth="2" className="w-7 h-7">
                  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                  <polyline points="17 6 23 6 23 12" />
                </svg>
              )}
              {stat.icon === "building" && (
                <svg viewBox="0 0 24 24" fill="none" stroke={stat.color === "success" ? "#10B981" : stat.color === "danger" ? "#EF4444" : stat.color === "warning" ? "#F59E0B" : "#3B82F6"} strokeWidth="2" className="w-7 h-7">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                  <polyline points="9 22 9 12 15 12 15 22" />
                </svg>
              )}
              {stat.icon === "alert" && (
                <svg viewBox="0 0 24 24" fill="none" stroke={stat.color === "success" ? "#10B981" : stat.color === "danger" ? "#EF4444" : stat.color === "warning" ? "#F59E0B" : "#3B82F6"} strokeWidth="2" className="w-7 h-7">
                  <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                  <path d="M12 9v4" />
                  <path d="M12 17h.01" />
                </svg>
              )}
              {stat.icon === "scan" && (
                <svg viewBox="0 0 24 24" fill="none" stroke={stat.color === "success" ? "#10B981" : stat.color === "danger" ? "#EF4444" : stat.color === "warning" ? "#F59E0B" : "#3B82F6"} strokeWidth="2" className="w-7 h-7">
                  <polyline points="23 4 23 10 17 10" />
                  <polyline points="1 20 1 14 7 14" />
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
                </svg>
              )}
            </div>
            <div className="text-sm font-medium text-gray-500 mb-1">{stat.label}</div>
            <div
              className={`text-4xl font-extrabold tracking-tight ${
                stat.color === "success"
                  ? "text-emerald-500"
                  : stat.color === "danger"
                  ? "text-red-500"
                  : stat.color === "warning"
                  ? "text-amber-500"
                  : "text-blue-500"
              }`}
            >
              {stat.value}
            </div>
          </div>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Recent Findings */}
        <div className="col-span-2 bg-white rounded-2xl shadow-md overflow-hidden animate-fade-in-up delay-500">
          <div className="p-6 border-b border-gray-100 flex justify-between items-center">
            <h2 className="text-lg font-bold">Recent Findings</h2>
            <Link
              href="/findings"
              className="flex items-center gap-2 px-4 py-2 bg-[#1E3A5F] text-white rounded-xl text-sm font-semibold hover:bg-[#0F2A4F] transition-colors"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              New Scan
            </Link>
          </div>
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Control</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Severity</th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentFindings.map((finding, idx) => (
                <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-semibold text-gray-800">{finding.control}</td>
                  <td className="px-6 py-4 text-gray-600">{finding.title}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                        finding.severityColor === "success"
                          ? "bg-emerald-100 text-emerald-700"
                          : finding.severityColor === "danger"
                          ? "bg-red-100 text-red-700"
                          : "bg-amber-100 text-amber-700"
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${
                        finding.severityColor === "success" ? "bg-emerald-500" : finding.severityColor === "danger" ? "bg-red-500" : "bg-amber-500"
                      }`} />
                      {finding.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold ${
                        finding.status === "Pass" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${finding.status === "Pass" ? "bg-emerald-500" : "bg-red-500"}`} />
                      {finding.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Severity Breakdown */}
        <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-600">
          <h2 className="text-lg font-bold mb-6">Findings by Severity</h2>
          <div className="space-y-4">
            {severityData.map((item) => (
              <div key={item.label} className="flex items-center gap-4">
                <div className="w-20 text-sm font-medium text-gray-600">{item.label}</div>
                <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${item.color} transition-all duration-1000`}
                    style={{ width: item.width }}
                  />
                </div>
                <div className="w-10 text-right font-bold text-gray-800">{item.count}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="bg-white rounded-2xl p-6 shadow-md animate-fade-in-up delay-600">
        <h2 className="text-lg font-bold mb-6">Recent Activity</h2>
        <div className="space-y-4">
          {activities.map((activity, idx) => (
            <div key={idx} className="flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors">
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  activity.type === "success"
                    ? "bg-emerald-100"
                    : activity.type === "danger"
                    ? "bg-red-100"
                    : "bg-blue-100"
                }`}
              >
                {activity.type === "success" && (
                  <svg viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2" className="w-5 h-5">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                )}
                {activity.type === "danger" && (
                  <svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" className="w-5 h-5">
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                  </svg>
                )}
                {activity.type === "info" && (
                  <svg viewBox="0 0 24 24" fill="none" stroke="#3B82F6" strokeWidth="2" className="w-5 h-5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                )}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-gray-800">{activity.title}</div>
                <div className="text-sm text-gray-500">{activity.desc}</div>
              </div>
              <div className="text-sm text-gray-400">{activity.time}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}