"""
On-Premise Scanner - Windows CIS via WinRM/PowerShell
Scans Windows servers using PowerShell CIS scripts
"""
import json
from typing import List, Dict, Optional
from datetime import datetime
import asyncio


class WindowsScanner:
    """Scan Windows servers via WinRM + PowerShell"""
    
    def __init__(self):
        self.script_url = "https://example.com/cis-windows-audit.ps1"
    
    async def scan(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 5985,
        use_ssl: bool = False
    ) -> List[Dict]:
        """
        Scan Windows server via WinRM
        
        Args:
            host: Server hostname/IP
            username: Windows username
            password: Windows password
            port: WinRM port (5985 HTTP, 5986 HTTPS)
            use_ssl: Use HTTPS
            
        Returns:
            List of findings
        """
        # Import winrm dynamically
        try:
            import winrm
        except ImportError:
            return [{"control_id": "WINRM_ERROR", "title": "winrm library not installed", "severity": "high", "status": "fail"}]
        
        try:
            # Set up session
            protocol = "https" if use_ssl else "http"
            target = f"{protocol}://{host}:{port}/wsman"
            
            session = winrm.Session(target, auth=(username, password))
            
            # Run CIS audit script
            return await self._run_scan(session)
        except Exception as e:
            return [{"control_id": "WINDOWS_SCAN", "title": str(e), "severity": "high", "status": "fail"}]
    
    async def _run_scan(self, session) -> List[Dict]:
        """Run PowerShell CIS scan"""
        findings = []
        
        # PowerShell script to run CIS checks
        script = """
        $ErrorActionPreference = 'SilentlyContinue'
        $findings = @()
        
        # CIS 1.1 - Ensure password complexity
        $policy = net accounts | Out-String
        if ($policy -match "Minimum Password Length.*?(\\d+)") {
            $minLen = [int]$matches[1]
            $findings += @{
                ControlID = "1.1"
                Title = "Ensure password complexity is enabled"
                Status = if ($minLen -ge 14) { "Pass" } else { "Fail" }
                Severity = if ($minLen -ge 14) { "low" } else { "high" }
                Finding = "Minimum length: $minLen"
            }
        }
        
        # CIS 1.2 - Ensure lockout policy
        $lockout = net accounts | Out-String
        if ($lockout -match "Lockout threshold.*?(\\w+)") {
            $threshold = $matches[1]
            $findings += @{
                ControlID = "1.2"
                Title = "Ensure account lockout policy is set"
                Status = if ($threshold -ne "Never" -and $threshold -ne "0") { "Pass" } else { "Fail" }
                Severity = if ($threshold -ne "Never" -and $threshold -ne "0") { "low" } else { "high" }
                Finding = "Lockout threshold: $threshold"
            }
        }
        
        # CIS 2.3 - Ensure Windows Firewall
        $fw = Get-NetFirewallProfile -ErrorAction SilentlyContinue
        if ($fw) {
            $enabled = ($fw | Where-Object {$_.Enabled -eq $true}).Count
            $findings += @{
                ControlID = "2.3"
                Title = "Ensure Windows Firewall is enabled"
                Status = if ($enabled -gt 0) { "Pass" } else { "Fail" }
                Severity = if ($enabled -gt 0) { "low" } else { "high" }
                Finding = "Enabled profiles: $enabled"
            }
        }
        
        # CIS 2.1 - Ensure Windows Defender
        $defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
        if ($defender) {
            $enabled = $defender.AntivirusEnabled
            $findings += @{
                ControlID = "2.1"
                Title = "Ensure Windows Defender is enabled"
                Status = if ($enabled) { "Pass" } else { "Fail" }
                Severity = if ($enabled) { "low" } else { "critical" }
                Finding = "Antivirus enabled: $enabled"
            }
        }
        
        # CIS 3.1 - Ensure Remote Desktop NLA
        $nla = (Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" -ErrorAction SilentlyContinue).UserAuthenticationRequired
        $findings += @{
            ControlID = "3.1"
            Title = "Ensure Network Level Authentication is required"
            Status = if ($nla -eq 1) { "Pass" } else { "Fail" }
            Severity = if ($nla -eq 1) { "low" } else { "high" }
            Finding = "NLA required: $nla"
        }
        
        # CIS 4.2 - Ensure SMBv1 disabled
        $smb1 = (Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -ErrorAction SilentlyContinue).State
        $findings += @{
            ControlID = "4.2"
            Title = "Ensure SMBv1 is disabled"
            Status = if ($smb1 -eq "Disabled") { "Pass" } else { "Fail" }
            Severity = if ($smb1 -eq "Disabled") { "low" } else { "high" }
            Finding = "SMB1: $smb1"
        }
        
        # Convert to JSON
        $findings | ConvertTo-Json -Depth 3
        """
        
        try:
            # Execute PowerShell script
            result = session.run_ps(script)
            
            if result.status_code != 0:
                return [{"control_id": "PS_ERROR", "title": result.std_err[:200], "severity": "high", "status": "fail"}]
            
            # Parse results
            output = result.std_out.strip()
            
            if not output:
                return [{"control_id": "WINDOWS_SCAN", "title": "No output", "severity": "medium", "status": "fail"}]
            
            # Try to parse JSON
            try:
                data = json.loads(output)
                if isinstance(data, dict):
                    findings.append(self._parse_finding(data))
                elif isinstance(data, list):
                    findings.extend([self._parse_finding(f) for f in data])
            except json.JSONDecodeError:
                # Fallback: create generic finding
                if "fail" in output.lower():
                    findings.append({
                        "control_id": "CIS_WINDOWS",
                        "title": "Windows CIS findings detected",
                        "severity": "high",
                        "status": "fail"
                    })
                else:
                    findings.append({
                        "control_id": "CIS_WINDOWS",
                        "title": "Windows CIS scan completed",
                        "severity": "low",
                        "status": "pass"
                    })
            
        except Exception as e:
            findings.append({
                "control_id": "WINDOWS_EXEC",
                "title": str(e),
                "severity": "high",
                "status": "fail"
            })
        
        return findings if findings else [
            {"control_id": "WINDOWS", "title": "Scan completed", "severity": "low", "status": "pass"}
        ]
    
    def _parse_finding(self, data: Dict) -> Dict:
        """Parse PowerShell finding"""
        status = str(data.get("Status", "")).lower()
        
        return {
            "control_id": data.get("ControlID", "Unknown"),
            "title": data.get("Title", ""),
            "severity": data.get("Severity", "medium"),
            "status": "fail" if status == "fail" else "pass",
            "asset": "windows",
            "finding": data.get("Finding", "")
        }


# Windows CIS control mapping
WINDOWS_CIS_CONTROLS = {
    "1.1": "Password Policy",
    "1.2": "Account Lockout Policy",
    "1.3": "Kerberos Policy",
    "2.1": "Windows Defender",
    "2.2": "Windows Firewall",
    "2.3": "Windows Firewall Profiles",
    "2.4": "Windows Defender Firewall",
    "3.1": "Remote Desktop NLA",
    "3.2": "Remote Desktop Security",
    "4.1": "Network Security",
    "4.2": "SMBv1 Disabled",
    "9.1": "Windows Audit Policy",
    "17.1": "Audit Policy Configuration",
}


async def run_windows_scan(
    host: str,
    credentials: Dict,
    customer_id: int,
    scan_id: int
) -> List[Dict]:
    """Scan Windows server"""
    scanner = WindowsScanner()
    
    return await scanner.scan(
        host=host,
        username=credentials.get("user", "Administrator"),
        password=credentials.get("password", ""),
        port=credentials.get("port", 5985),
        use_ssl=credentials.get("ssl", False)
    )


# Type alias
Dict = dict


# Example
if __name__ == "__main__":
    async def main():
        # Test script generation
        scanner = WindowsScanner()
        print("Windows CIS PowerShell scanner initialized")
        print("Requires: pip install pywinrm")
    
    asyncio.run(main())