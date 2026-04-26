"""
AWS Scanner - SSM RunCommand Scanner
Executes OpenSCAP via SSM RunCommand on EC2 instances
"""
import boto3
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from botocore.exceptions import ClientError


class SSMScanner:
    """Execute scans via SSM RunCommand"""
    
    def __init__(self, credentials: Dict, region: str = "us-east-1"):
        self.region = region
        
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials.get("SessionToken"),
            region_name=region
        )
        
        self.ssm = session.client("ssm")
        self.ec2 = session.client("ec2")
        self.sts = session.client("sts")
    
    async def get_linux_instances(self) -> List[Dict]:
        """Get Linux EC2 instances"""
        try:
            response = self.ec2.describe_instances(
                Filters=[
                    {"Name": "instance-state-name", "Values": ["running"]},
                    {"Name": "platform", "Values": ["linux"]}
                ]
            )
            
            instances = []
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    # Check if SSM agent is installed
                    if instance.get("State", {}).get("Name") == "running":
                        instances.append({
                            "instance_id": instance["InstanceId"],
                            "image_id": instance.get("ImageId", ""),
                            "instance_type": instance.get("InstanceType", ""),
                            "private_ip": instance.get("PrivateIpAddress", ""),
                            "tags": {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
                        })
            
            return instances
        except ClientError as e:
            print(f"Error describing instances: {e}")
            return []
    
    async def get_windows_instances(self) -> List[Dict]:
        """Get Windows EC2 instances"""
        try:
            response = self.ec2.describe_instances(
                Filters=[
                    {"Name": "instance-state-name", "Values": ["running"]},
                    {"Name": "platform", "Values": ["windows"]}
                ]
            )
            
            instances = []
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    if instance.get("State", {}).get("Name") == "running":
                        instances.append({
                            "instance_id": instance["InstanceId"],
                            "image_id": instance.get("ImageId", ""),
                            "instance_type": instance.get("InstanceType", ""),
                            "private_ip": instance.get("PrivateIpAddress", ""),
                            "tags": {t["Key"]: t["Value"] for t in instance.get("Tags", [])}
                        })
            
            return instances
        except ClientError as e:
            print(f"Error describing instances: {e}")
            return []
    
    async def scan_linux(self, instance_id: str) -> List[Dict]:
        """Run OpenSCAP on Linux instance"""
        try:
            # Run OpenSCAP via SSM
            command_id = await self._send_command(
                instance_id,
                "aws:runShellScript",
                "Run OpenSCAP CIS Benchmark",
                [
                    "yum install -y openscap-scanner",
                    "oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis "
                    "/usr/share/xml/scap/ssg-*/ds/ssg-*-ds.xml --results /tmp/scap-results.xml"
                ]
            )
            
            if not command_id:
                return [{"control_id": "SCAN_ERROR", "title": "Failed to send command", "severity": "high", "status": "fail"}]
            
            # Wait for command completion
            await asyncio.sleep(60)  # Wait for scan to complete
            
            # Get results
            results = await self._get_command_output(instance_id, command_id)
            
            return self._parse_openscap_results(results)
            
        except Exception as e:
            return [{"control_id": "LINUX_SCAN", "title": str(e), "severity": "high", "status": "fail"}]
    
    async def scan_windows(self, instance_id: str) -> List[Dict]:
        """Run PowerShell CIS checks on Windows instance"""
        try:
            # Run PowerShell CIS script via SSM
            command_id = await self._send_command(
                instance_id,
                "aws:runPowerShellScript",
                "Run CIS Windows Benchmark",
                [
                    # Download CIS script
                    "Invoke-WebRequest -Uri 'https://example.com/cis-audit.ps1' -OutFile C:\\cis-audit.ps1",
                    # Run CIS audit
                    "& C:\\cis-audit.ps1 -OutputPath C:\\cis-results.json"
                ]
            )
            
            if not command_id:
                return [{"control_id": "SCAN_ERROR", "title": "Failed to send command", "severity": "high", "status": "fail"}]
            
            # Wait for command completion
            await asyncio.sleep(120)  # Windows scans take longer
            
            # Get results
            results = await self._get_command_output(instance_id, command_id)
            
            return self._parse_powershell_results(results)
            
        except Exception as e:
            return [{"control_id": "WINDOWS_SCAN", "title": str(e), "severity": "high", "status": "fail"}]
    
    async def _send_command(
        self, 
        instance_id: str, 
        document: str, 
        comment: str,
        commands: List[str]
    ) -> Optional[str]:
        """Send SSM command"""
        try:
            response = self.ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName=document,
                Comment=comment,
                Parameters={"commands": commands},
                TimeoutSeconds=300
            )
            
            return response["Command"]["CommandId"]
        except ClientError as e:
            print(f"Error sending command: {e}")
            return None
    
    async def _get_command_output(self, instance_id: str, command_id: str) -> str:
        """Get command output"""
        try:
            # Wait for command to complete
            for _ in range(30):
                response = self.ssm.get_command_invocation(
                    InstanceId=instance_id,
                    CommandId=command_id
                )
                
                status = response["Status"]
                if status in ("Success", "Failed", "TimedOut"):
                    break
                
                await asyncio.sleep(10)
            
            # Get output
            response = self.ssm.get_command_invocation(
                InstanceId=instance_id,
                CommandId=command_id
            )
            
            return response.get("Output", "")
            
        except ClientError as e:
            print(f"Error getting output: {e}")
            return ""
    
    def _parse_openscap_results(self, output: str) -> List[Dict]:
        """Parse OpenSCAP XML results"""
        findings = []
        
        # Simple parsing - in production, use XML parser
        if "fail" in output.lower() or "failed" in output.lower():
            findings.append({
                "control_id": "openscap",
                "title": "OpenSCAP CIS findings detected",
                "severity": "high",
                "status": "fail",
                "asset": "EC2",
                "finding": output[:500]
            })
        else:
            findings.append({
                "control_id": "openscap",
                "title": "OpenSCAP scan completed",
                "severity": "low",
                "status": "pass",
                "asset": "EC2"
            })
        
        return findings
    
    def _parse_powershell_results(self, output: str) -> List[Dict]:
        """Parse PowerShell CIS results"""
        findings = []
        
        # Try to parse JSON results
        try:
            results = json.loads(output)
            
            for result in results:
                findings.append({
                    "control_id": result.get("ControlID", "Unknown"),
                    "title": result.get("Description", ""),
                    "severity": result.get("Severity", "medium"),
                    "status": "fail" if result.get("Status") == "Fail" else "pass",
                    "asset": result.get("ComputerName", "Unknown"),
                    "finding": result.get("Finding", "")
                })
        except json.JSONDecodeError:
            # Fallback to text parsing
            if "fail" in output.lower():
                findings.append({
                    "control_id": "CIS_WINDOWS",
                    "title": "Windows CIS findings detected",
                    "severity": "high",
                    "status": "fail",
                    "asset": "EC2"
                })
            else:
                findings.append({
                    "control_id": "CIS_WINDOWS",
                    "title": "Windows CIS scan completed",
                    "severity": "low",
                    "status": "pass",
                    "asset": "EC2"
                })
        
        return findings


async def run_ssm_scan(
    credentials: Dict,
    instance_ids: List[str],
    region: str = "us-east-1"
) -> List[Dict]:
    """Run SSM scans on instances"""
    scanner = SSMScanner(credentials, region)
    
    all_findings = []
    
    for instance_id in instance_ids:
        # Determine OS type
        try:
            ec2 = boto3.client("ec2")
            response = ec2.describe_instances(InstanceIds=[instance_id])
            instance = response["Reservations"][0]["Instances"][0]
            platform = instance.get("Platform", "linux")
            
            if platform == "windows":
                findings = await scanner.scan_windows(instance_id)
            else:
                findings = await scanner.scan_linux(instance_id)
            
            all_findings.extend(findings)
            
        except Exception as e:
            all_findings.append({
                "control_id": "SSM_ERROR",
                "title": str(e),
                "severity": "high",
                "status": "error",
                "asset": instance_id
            })
    
    return all_findings


# Example
if __name__ == "__main__":
    async def main():
        creds = {
            "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
            "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        }
        
        scanner = SSMScanner(creds)
        
        # Get Linux instances
        linux_instances = await scanner.get_linux_instances()
        print(f"Found {len(linux_instances)} Linux instances")
        
        for inst in linux_instances[:5]:
            print(f"  {inst['instance_id']}: {inst.get('tags', {}).get('Name', 'unnamed')}")
    
    asyncio.run(main())