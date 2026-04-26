"""
AWS Scanner - Prowler CLI Integration
Runs CIS AWS Foundations benchmark using Prowler
"""
import asyncio
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError


class ProwlerScanner:
    """Prowler CLI wrapper for AWS CIS scanning"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.prowler_path = os.getenv("PROWLER_PATH", "/usr/local/bin")
    
    async def scan(
        self, 
        account_id: str, 
        role_arn: str, 
        external_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Run Prowler scan for an AWS account
        
        Args:
            account_id: AWS Account ID
            role_arn: Cross-account IAM Role ARN
            external_id: External ID for cross-account access
            
        Returns:
            List of findings
        """
        # Assume role
        credentials = await self._assume_role(account_id, role_arn, external_id)
        if not credentials:
            return [{"error": "Failed to assume role", "severity": "high"}]
        
        # Set environment for Prowler
        env = os.environ.copy()
        env["AWS_ACCESS_KEY_ID"] = credentials["AccessKeyId"]
        env["AWS_SECRET_ACCESS_KEY"] = credentials["SecretAccessKey"]
        env["AWS_SESSION_TOKEN"] = credentials["SessionToken"]
        
        # Run Prowler
        result = await self._run_prowler(env)
        
        return result
    
    async def _assume_role(
        self, 
        account_id: str, 
        role_arn: str, 
        external_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Assume cross-account role"""
        try:
            sts = boto3.client("sts")
            
            kwargs = {
                "RoleArn": role_arn,
                "RoleSessionName": f"compliance-scan-{account_id}"
            }
            
            if external_id:
                kwargs["ExternalId"] = external_id
            
            response = sts.assume_role(**kwargs)
            
            return {
                "AccessKeyId": response["Credentials"]["AccessKeyId"],
                "SecretAccessKey": response["Credentials"]["SecretAccessKey"],
                "SessionToken": response["Credentials"]["SessionToken"]
            }
        except ClientError as e:
            print(f"Failed to assume role: {e}")
            return None
    
    async def _run_prowler(self, env: Dict) -> List[Dict]:
        """Execute Prowler CLI"""
        cmd = [
            os.path.join(self.prowler_path, "prowler"),
            "-r", self.region,
            "-M", "json",
            "-f", "json",
            "--output-json"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"Prowler error: {stderr.decode()}")
                return []
            
            # Parse JSON output
            findings = []
            for line in stdout.decode().split("\n"):
                if line.strip():
                    try:
                        findings.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return findings
            
        except FileNotFoundError:
            return [{"error": "Prowler not found", "severity": "high"}]
        except Exception as e:
            return [{"error": str(e), "severity": "high"}]


# CIS AWS Foundations control mapping
CIS_AWS_CONTROLS = {
    "1.1": "Initial Setup",
    "1.2": "Initial Setup", 
    "1.3": "Initial Setup",
    "1.4": "Initial Setup",
    "1.5": "Initial Setup",
    "1.6": "Initial Setup",
    "1.7": "Initial Setup",
    "1.8": "Initial Setup",
    "1.9": "Initial Setup",
    "1.10": "Initial Setup",
    "1.11": "Initial Setup",
    "1.12": "Initial Setup",
    "1.13": "Initial Setup",
    "1.14": "Initial Setup",
    "1.15": "Initial Setup",
    "1.16": "Initial Setup",
    "1.17": "Initial Setup",
    "1.18": "Initial Setup",
    "1.19": "Initial Setup",
    "1.20": "Initial Setup",
    "1.21": "Initial Setup",
    "1.22": "Initial Setup",
    "2.1": "Logging and Monitoring",
    "2.2": "Logging and Monitoring",
    "2.3": "Logging and Monitoring",
    "2.4": "Logging and Monitoring",
    "2.5": "Logging and Monitoring",
    "2.6": "Logging and Monitoring",
    "2.7": "Logging and Monitoring",
    "2.8": "Logging and Monitoring",
    "2.9": "Logging and Monitoring",
    "2.10": "Logging and Monitoring",
    "3.1": "Networking",
    "3.2": "Networking",
    "3.3": "Networking",
    "3.4": "Networking",
    "3.5": "Networking",
    "3.6": "Networking",
    "3.7": "Networking",
    "3.8": "Networking",
    "3.9": "Networking",
    "3.10": "Networking",
    "3.11": "Networking",
    "4.1": "Storage",
    "4.2": "Storage",
    "4.3": "Storage",
    "4.4": "Storage",
    "4.5": "Storage",
    "4.6": "Storage",
    "4.7": "Storage",
    "4.8": "Storage",
    "4.9": "Storage",
    "4.10": "Storage",
    "4.11": "Storage",
    "4.12": "Storage",
    "4.13": "Storage",
    "5.1": "IAM",
    "5.2": "IAM",
    "5.3": "IAM",
    "5.4": "IAM",
    "5.5": "IAM",
    "5.6": "IAM",
    "5.7": "IAM",
    "5.8": "IAM",
    "5.9": "IAM",
}


def parse_prowler_finding(finding: Dict) -> Dict:
    """
    Parse Prowler finding to standard format
    
    Args:
        finding: Raw Prowler finding
        
    Returns:
        Normalized finding
    """
    # Extract severity
    severity = "medium"
    if "FAIL" in str(finding.get("status", "")).upper():
        severity = "high"
    
    # Extract control ID
    control_id = ""
    result_id = str(finding.get("ResultId", ""))
    if "[" in result_id:
        control_id = result_id.split("[")[1].split("]")[0]
    elif result_id.startswith("["):
        control_id = result_id[1:result_id.index("]")]
    
    return {
        "control_id": control_id or finding.get("CheckId", ""),
        "title": finding.get("CheckTitle", finding.get("ServiceName", "Unknown")),
        "description": finding.get("Description", ""),
        "severity": finding.get("Risk", severity),
        "status": "fail" if "FAIL" in str(finding.get("Status", "")).upper() else "pass",
        "asset": finding.get("ResourceName", finding.get("ResourceId", "")),
        "region": finding.get("Region", ""),
        "account": finding.get("AccountId", ""),
        "timestamp": finding.get("Timestamp", datetime.utcnow().isoformat()),
        "raw": finding
    }


async def run_aws_scan(
    account_id: str,
    role_arn: str,
    customer_id: int,
    scan_id: int,
    region: str = "us-east-1"
) -> List[Dict]:
    """
    Main entry point for AWS scanning
    
    Args:
        account_id: AWS Account ID
        role_arn: Cross-account role ARN
        customer_id: Internal customer ID
        scan_id: Internal scan ID
        region: AWS region
        
    Returns:
        List of findings in standard format
    """
    scanner = ProwlerScanner(region=region)
    
    findings = await scanner.scan(account_id, role_arn)
    
    # Parse findings
    parsed = []
    for f in findings:
        if "error" in f:
            parsed.append({
                "control_id": "SCAN_ERROR",
                "title": f["error"],
                "severity": "high",
                "status": "fail"
            })
        else:
            parsed.append(parse_prowler_finding(f))
    
    return parsed


# Example usage
if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) < 3:
            print("Usage: python prowler.py <account_id> <role_arn>")
            return
        
        account_id = sys.argv[1]
        role_arn = sys.argv[2]
        
        findings = await run_aws_scan(account_id, role_arn, 1, 1)
        
        print(f"Found {len(findings)} findings")
        for f in findings[:10]:
            print(f"  [{f['severity']}] {f['control_id']}: {f['title']}")
    
    asyncio.run(main())