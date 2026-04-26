"""
Drift Detection Engine
Compares scan results to detect compliance drift
"""
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DriftResult:
    """Drift detection result"""
    new_failures: List[Dict]
    new_passes: List[Dict]
    severity_increases: List[Dict]
    severity_decreases: List[Dict]
    removed_assets: List[Dict]
    new_assets: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            "new_failures": self.new_failures,
            "new_passes": self.new_passes,
            "severity_increases": self.severity_increases,
            "severity_decreases": self.severity_decreases,
            "removed_assets": self.removed_assets,
            "new_assets": self.new_assets
        }


class DriftEngine:
    """Detect compliance drift between scans"""
    
    SEVERITY_ORDER = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "info": 0
    }
    
    def compare(
        self,
        current_findings: List[Dict],
        previous_findings: List[Dict]
    ) -> DriftResult:
        """
        Compare two scan results to detect drift
        
        Args:
            current_findings: Current scan findings
            previous_findings: Previous scan findings
            
        Returns:
            DriftResult with changes
        """
        # Index by control_id + asset for comparison
        current_map = {
            (f.get("control_id"), f.get("asset", "")): f 
            for f in current_findings
        }
        previous_map = {
            (f.get("control_id"), f.get("asset", "")): f 
            for f in previous_findings
        }
        
        current_keys = set(current_map.keys())
        previous_keys = set(previous_map.keys())
        
        # New failures (now failing, was passing)
        new_failures = []
        for key in current_keys - previous_keys:
            finding = current_map[key]
            if finding.get("status") == "fail":
                new_failures.append(finding)
        
        # New passes (now passing, was failing)  
        new_passes = []
        for key in previous_keys - current_keys:
            finding = previous_map[key]
            if finding.get("status") == "fail":
                new_passes.append(finding)
        
        # Severity increases (same control, worse severity)
        severity_increases = []
        severity_decreases = []
        
        for key in current_keys & previous_keys:
            curr = current_map[key]
            prev = previous_map[key]
            
            curr_sev = self.SEVERITY_ORDER.get(curr.get("severity", "low"), 1)
            prev_sev = self.SEVERITY_ORDER.get(prev.get("severity", "low"), 1)
            
            if curr_sev > prev_sev:
                severity_increases.append({
                    "control_id": curr.get("control_id"),
                    "asset": curr.get("asset"),
                    "previous_severity": prev.get("severity"),
                    "current_severity": curr.get("severity"),
                    "finding": curr
                })
            elif curr_sev < prev_sev:
                severity_decreases.append({
                    "control_id": curr.get("control_id"),
                    "asset": curr.get("asset"),
                    "previous_severity": prev.get("severity"),
                    "current_severity": curr.get("severity"),
                    "finding": curr
                })
        
        # Find assets that were in previous but not current (removed)
        removed_assets = [
            {"control_id": previous_map[k].get("control_id"), "asset": k[1]}
            for k in previous_keys - current_keys
        ]
        
        # Find new assets (new since previous)
        new_assets = [
            {"control_id": current_map[k].get("control_id"), "asset": k[1]}
            for k in current_keys - previous_keys
        ]
        
        return DriftResult(
            new_failures=new_failures,
            new_passes=new_passes,
            severity_increases=severity_increases,
            severity_decreases=severity_decreases,
            removed_assets=removed_assets,
            new_assets=new_assets
        )
    
    def calculate_compliance_score(self, findings: List[Dict]) -> float:
        """Calculate compliance score (0-100)"""
        if not findings:
            return 100.0
        
        passed = sum(1 for f in findings if f.get("status") == "pass")
        total = len(findings)
        
        return round((passed / total) * 100, 1) if total > 0 else 100.0
    
    def get_summary(self, drift: DriftResult) -> Dict:
        """Get drift summary"""
        total_changes = (
            len(drift.new_failures) +
            len(drift.new_passes) +
            len(drift.severity_increases) +
            len(drift.severity_decreases)
        )
        
        # Score impact
        score_change = 0
        score_change -= len(drift.new_failures) * 10
        score_change += len(drift.new_passes) * 10
        score_change -= len(drift.severity_increases) * 5
        score_change += len(drift.severity_decreases) * 5
        
        return {
            "total_changes": total_changes,
            "score_change": score_change,
            "new_failures_count": len(drift.new_failures),
            "new_passes_count": len(drift.new_passes),
            "severity_increases_count": len(drift.severity_increases),
            "severity_decreases_count": len(drift.severity_decreases),
            "new_assets_count": len(drift.new_assets),
            "removed_assets_count": len(drift.removed_assets),
            "status": "improved" if score_change > 0 else "degraded" if score_change < 0 else "stable"
        }


# Helper functions

async def detect_scan_drift(
    db_pool,
    customer_id: int,
    scan_id: int
) -> Dict:
    """Detect drift for a customer between current and previous scan"""
    
    from datetime import timedelta
    
    async with db_pool.acquire() as conn:
        # Get current scan findings
        current = await conn.fetch("""
            SELECT control_id, title, severity, status, asset
            FROM findings 
            WHERE customer_id = $1 AND scan_id = $2
        """, customer_id, scan_id)
        
        # Get previous scan findings (last completed scan before current)
        previous_info = await conn.fetchrow("""
            SELECT id FROM scans 
            WHERE customer_id = $1 AND status = 'completed' AND id < $2
            ORDER BY completed_at DESC LIMIT 1
        """, customer_id, scan_id)
        
        if not previous_info:
            return {"drift": None, "message": "No previous scan"}
        
        previous = await conn.fetch("""
            SELECT control_id, title, severity, status, asset
            FROM findings 
            WHERE customer_id = $1 AND scan_id = $2
        """, customer_id, previous_info["id"])
        
        # Compare
        engine = DriftEngine()
        drift = engine.compare(
            [dict(f) for f in current],
            [dict(f) for f in previous]
        )
        
        summary = engine.get_summary(drift)
        
        return {
            "drift": drift.to_dict(),
            "summary": summary,
            "current_score": engine.calculate_compliance_score([dict(f) for f in current]),
            "previous_score": engine.calculate_compliance_score([dict(f) for f in previous])
        }


# Example
if __name__ == "__main__":
    # Test drift detection
    current = [
        {"control_id": "1.1", "status": "fail", "severity": "high", "asset": "host1"},
        {"control_id": "1.2", "status": "pass", "severity": "low", "asset": "host1"},
        {"control_id": "1.3", "status": "fail", "severity": "critical", "asset": "host2"},
    ]
    
    previous = [
        {"control_id": "1.1", "status": "pass", "severity": "low", "asset": "host1"},
        {"control_id": "1.2", "status": "pass", "severity": "low", "asset": "host1"},
    ]
    
    engine = DriftEngine()
    drift = engine.compare(current, previous)
    summary = engine.get_summary(drift)
    
    print("Drift Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")