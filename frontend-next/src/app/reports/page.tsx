"use client";

const reports = [
  { id: 1, title: "Acme Corp - Q1 2026", type: "Quarterly", date: "2026-04-01", score: 92, pages: 24 },
  { id: 2, title: "Beta Inc - April 2026", type: "Monthly", date: "2026-04-18", score: 78, pages: 18 },
  { id: 3, title: "GlobalTech - Q1 2026", type: "Quarterly", date: "2026-04-10", score: 95, pages: 28 },
  { id: 4, title: "Acme Corp - Drift Report", type: "Drift", date: "2026-04-15", score: null, pages: 8 },
  { id: 5, title: "Executive Summary - Q1", type: "Executive", date: "2026-04-01", score: null, pages: 12 },
  { id: 6, title: "Security Audit - Acme", type: "Audit", date: "2026-04-12", score: 89, pages: 32 },
];

export default function ReportsPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center animate-slide-down">
        <div>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Reports</h1>
          <p className="text-gray-500 mt-1">View and download compliance reports</p>
        </div>
        <button className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#1E3A5F] to-[#0F2A4F] text-white rounded-2xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="18" x2="12" y2="12" />
            <line x1="9" y1="15" x2="15" y2="15" />
          </svg>
          Generate Report
        </button>
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-3 gap-6">
        {reports.map((report, idx) => (
          <div
            key={report.id}
            className="bg-white rounded-2xl shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 animate-fade-in-up"
            style={{ animationDelay: `${idx * 0.1}s` }}
          >
            {/* Preview */}
            <div className="h-48 bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMtOS45NDEgMC0xOCA4LjA1OS0xOCAxOHM4LjA1OSAxOCAxOCAxOCAxOC04LjA1OSAxOC0xOC04LjA1OS0xOC0xOC0xOHptMCAzMmMtNy43MzIgMC0xNC02LjI2OC0xNC0xNHM2LjI2OC0xNCAxNC0xNCAxNCA2LjI2OCAxNCAxNC02LjI2OCAxNC0xNCAxNHoiIGZpbGw9IiNjY2MiIGZpbGwtb3BhY2l0eT0iLjEiLz48L2c+PC9zdmc+')] opacity-50" />
              <div className="w-32 h-40 bg-white rounded-lg shadow-lg flex flex-col p-3 relative z-10">
                <div className="h-2 bg-gray-200 rounded mb-2" />
                <div className="h-1.5 bg-gray-100 rounded mb-1" />
                <div className="h-1.5 bg-gray-100 rounded mb-1" />
                <div className="h-1.5 bg-gray-100 rounded mb-1" />
                <div className="h-1.5 bg-gray-100 rounded mb-2" />
                <div className="h-1 bg-gray-100 rounded" />
                <div className="flex-1" />
                <div className="h-3 bg-[#1E3A5F] rounded" />
              </div>
            </div>
            
            {/* Info */}
            <div className="p-5">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-gray-800 text-sm">{report.title}</h3>
                <span className="px-2 py-1 bg-gray-100 rounded text-xs text-gray-600">{report.type}</span>
              </div>
              <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                <span>{report.date}</span>
                {report.score && <span className="font-semibold text-emerald-600">{report.score}%</span>}
              </div>
              <div className="flex gap-2">
                <button className="flex-1 py-2 bg-[#1E3A5F] text-white rounded-lg text-sm font-medium hover:bg-[#0F2A4F] transition-colors flex items-center justify-center gap-2">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="7 10 12 15 17 10" />
                    <line x1="12" y1="15" x2="12" y2="3" />
                  </svg>
                  Download
                </button>
                <button className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-colors">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}