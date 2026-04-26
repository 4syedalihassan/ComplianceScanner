"""
Report Generator - PDF Reports via Jinja2 + WeasyPrint
"""
import boto3
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from typing import Dict, List, Optional
import io
from datetime import datetime
import json


class ReportGenerator:
    """Generate PDF compliance reports"""
    
    def __init__(
        self,
        template_dir: str = "src/reports/templates",
        s3_bucket: str = None,
        aws_region: str = "us-east-1"
    ):
        self.template_dir = template_dir
        self.s3_bucket = s3_bucket
        self.aws_region = aws_region
        
        # Setup Jinja2
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # S3 client
        self.s3_client = None
        if s3_bucket:
            self.s3_client = boto3.client('s3', region_name=aws_region)
    
    async def generate_report(
        self,
        customer_id: int,
        scan_id: int,
        findings: List[Dict],
        previous_findings: Optional[List[Dict]] = None
    ) -> bytes:
        """
        Generate PDF report
        
        Args:
            customer_id: Customer ID
            scan_id: Scan ID
            findings: Current findings
            previous_findings: Previous scan findings for comparison
            
        Returns:
            PDF bytes
        """
        # Calculate scores
        current_score = self._calculate_score(findings)
        previous_score = self._calculate_score(previous_findings) if previous_findings else None
        
        # Categorize findings
        by_severity = self._categorize_by_severity(findings)
        by_control = self._categorize_by_control(findings)
        
        # Drift analysis
        drift = None
        if previous_findings:
            drift = self._calculate_drift(findings, previous_findings)
        
        # Render template
        template = self.env.get_template("report.html")
        html = template.render(
            customer_id=customer_id,
            scan_id=scan_id,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            current_score=current_score,
            previous_score=previous_score,
            score_change=current_score - previous_score if previous_score else None,
            total_findings=len(findings),
            by_severity=by_severity,
            by_control=by_control,
            findings=findings[:100],  # Limit for PDF
            drift=drift
        )
        
        # Convert to PDF
        pdf = HTML(string=html).write_pdf()
        
        return pdf
    
    async def save_to_s3(self, pdf: bytes, customer_id: int, scan_id: int) -> str:
        """Save report to S3"""
        if not self.s3_client or not self.s3_bucket:
            return None
        
        key = f"reports/{customer_id}/{scan_id}/{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=pdf,
            ContentType='application/pdf',
            ServerSideEncryption='AES256'
        )
        
        # Return S3 URL
        return f"s3://{self.s3_bucket}/{key}"
    
    def _calculate_score(self, findings: List[Dict]) -> float:
        """Calculate compliance score"""
        if not findings:
            return 100.0
        
        passed = sum(1 for f in findings if f.get("status") == "pass")
        total = len(findings)
        
        return round((passed / total) * 100, 1) if total > 0 else 100.0
    
    def _categorize_by_severity(self, findings: List[Dict]) -> Dict:
        """Group findings by severity"""
        categories = {"critical": [], "high": [], "medium": [], "low": [], "info": []}
        
        for f in findings:
            sev = f.get("severity", "low")
            if sev in categories:
                categories[sev].append(f)
        
        return {k: len(v) for k, v in categories.items()}
    
    def _categorize_by_control(self, findings: List[Dict]) -> Dict:
        """Group findings by control"""
        categories = {}
        
        for f in findings:
            control = f.get("control_id", "Unknown")
            prefix = control.split(".")[0] if "." in control else control[:3]
            
            if prefix not in categories:
                categories[prefix] = []
            categories[prefix].append(f)
        
        return {k: len(v) for k, v in categories.items()}
    
    def _calculate_drift(self, current: List[Dict], previous: List[Dict]) -> Dict:
        """Calculate drift from previous scan"""
        current_ids = {(f.get("control_id"), f.get("asset", "")) for f in current}
        previous_ids = {(f.get("control_id"), f.get("asset", "")) for f in previous}
        
        new_failures = len(current_ids - previous_ids)
        new_passes = len(previous_ids - current_ids)
        
        return {
            "new_failures": new_failures,
            "new_passes": new_passes,
            "status": "improved" if new_passes > new_failures else "degraded" if new_failures > new_passes else "stable"
        }


# Report template (HTML)
REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Compliance Report - Customer {{customer_id}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { border-bottom: 2px solid #1E3A5F; padding-bottom: 20px; margin-bottom: 30px; }
        .score { font-size: 48px; font-weight: bold; }
        .score-good { color: #2e7d32; }
        .score-medium { color: #f9a825; }
        .score-bad { color: #c62828; }
        .section { margin: 30px 0; }
        .findings-table { width: 100%; border-collapse: collapse; }
        .findings-table th, .findings-table td { 
            border: 1px solid #ddd; padding: 8px; text-align: left; 
        }
        .findings-table th { background: #1E3A5F; color: white; }
        .severity-critical { background: #ffcdd2; }
        .severity-high { background: #ffecce; }
        .severity-medium { background: #fff9c4; }
        .severity-low { background: #e8f5e9; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Compliance Report</h1>
        <p>Customer ID: {{customer_id}} | Scan ID: {{scan_id}}</p>
        <p>Generated: {{generated_at}}</p>
    </div>
    
    <div class="section">
        <h2>Executive Summary</h2>
        <div class="score {% if current_score >= 80 %}score-good{% elif current_score >= 60 %}score-medium{% else %}score-bad{% endif %}">
            {{current_score}}%
        </div>
        <p>Compliance Score{% if previous_score %}(previous: {{previous_score}}%, change: {{score_change}}%){% endif %}</p>
        <p>Total Findings: {{total_findings}}</p>
    </div>
    
    <div class="section">
        <h2>Findings by Severity</h2>
        <ul>
            <li>Critical: {{by_severity.critical}}</li>
            <li>High: {{by_severity.high}}</li>
            <li>Medium: {{by_severity.medium}}</li>
            <li>Low: {{by_severity.low}}</li>
            <li>Info: {{by_severity.info}}</li>
        </ul>
    </div>
    
    {% if drift %}
    <div class="section">
        <h2>Drift Analysis</h2>
        <p>Status: {{drift.status}}</p>
        <p>New Failures: {{drift.new_failures}} | New Passes: {{drift.new_passes}}</p>
    </div>
    {% endif %}
    
    <div class="section">
        <h2>Findings Detail</h2>
        <table class="findings-table">
            <tr>
                <th>Control</th>
                <th>Title</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Asset</th>
            </tr>
            {% for f in findings %}
            <tr class="severity-{{f.severity}}">
                <td>{{f.control_id}}</td>
                <td>{{f.title[:60]}}{% if f.title|length > 60 %}...{% endif %}</td>
                <td>{{f.severity}}</td>
                <td>{{f.status}}</td>
                <td>{{f.asset}}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""


# Helper to create default template
def create_default_template(template_dir: str):
    """Create default report template"""
    import os
    os.makedirs(template_dir, exist_ok=True)
    
    template_path = os.path.join(template_dir, "report.html")
    with open(template_path, "w") as f:
        f.write(REPORT_TEMPLATE)
    
    return template_path


# Example usage
if __name__ == "__main__":
    print("Report generator ready")
    print("Use create_default_template() to create HTML template")