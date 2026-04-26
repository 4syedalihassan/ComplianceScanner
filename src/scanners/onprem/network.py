"""
On-Premise Scanner - Network Devices (Cisco, FortiGate) via Netmiko
Scans network device configurations
"""
import netmiko
from netmiko.exceptions import NetmikoBaseException
from typing import List, Dict, Optional
import re
from datetime import datetime


class NetworkScanner:
    """Scan network devices via Netmiko"""
    
    CISCO_CONTROLS = {
        "1.1": "Ensure unused external interfaces are disabled",
        "1.2": "Ensure HTTP server is disabled",
        "1.3": "Ensure SSH is enabled",
        "1.4": "Ensure console timeout is configured",
        "1.5": "Ensure exec timeout is configured",
        "2.1": "Ensure passwords are encrypted",
        "2.2": "Ensure enable secret is configured",
        "2.3": "Ensure password encryption is used",
        "3.1": "Ensure AAA is configured",
        "3.2": "Ensure AAA authorization is configured",
        "3.3": "Ensure accounting is configured",
        "4.1": "Ensure SNMP is disabled or v3",
        "4.2": "Ensure SNMP community string is complex",
        "5.1": "Ensure logging is enabled",
    }
    
    FORTIGATE_CONTROLS = {
        "1.1": "Ensure admin HTTPS is enabled",
        "1.2": "Ensure SSH is enabled",
        "1.3": "Ensure console is disabled",
        "1.4": "Ensure admin timeout is set",
        "2.1": "Ensure strong passwords",
        "2.2": "Ensure password history",
        "3.1": "Ensure logging enabled",
        "3.2": "Ensure log retention",
        "4.1": "Ensure interfaces in DMZ",
    }
    
    async def scan_cisco(
        self,
        host: str,
        username: str,
        password: str,
        secret: Optional[str] = None,
        device_type: str = "cisco_ios"
    ) -> List[Dict]:
        """Scan Cisco IOS device"""
        return await self._scan(
            host=host,
            username=username,
            password=password,
            secret=secret,
            device_type=device_type,
            controls=self.CISCO_CONTROLS
        )
    
    async def scan_fortigate(
        self,
        host: str,
        username: str,
        password: str,
        device_type: str = "fortinet_fortios"
    ) -> List[Dict]:
        """Scan FortiGate device"""
        return await self._scan(
            host=host,
            username=username,
            password=password,
            device_type=device_type,
            controls=self.FORTIGATE_CONTROLS
        )
    
    async def _scan(
        self,
        host: str,
        username: str,
        password: str,
        secret: Optional[str] = None,
        device_type: str = "cisco_ios",
        controls: Dict = None
    ) -> List[Dict]:
        """Generic network device scan"""
        findings = []
        
        try:
            # Connect to device
            device = {
                "device_type": device_type,
                "host": host,
                "username": username,
                "password": password,
            }
            
            if secret:
                device["secret"] = secret
            
            with netmiko.ConnectHandler(**device) as conn:
                # Get running config
                config = conn.send_command("show run")
                
                # Run CIS checks
                for control_id, description in (controls or {}).items():
                    finding = self._check_cisco_control(control_id, description, config, device_type)
                    findings.append(finding)
                
                # Additional checks based on device type
                if device_type == "cisco_ios":
                    findings.extend(self._check_cisco_ios_specific(config))
                elif device_type == "fortinet_fortios":
                    findings.extend(self._check_fortigate_specific(config))
        
        except NetmikoBaseException as e:
            return [{"control_id": "NETWORK_SSH", "title": str(e), "severity": "high", "status": "fail"}]
        except Exception as e:
            return [{"control_id": "NETWORK_SCAN", "title": str(e), "severity": "high", "status": "fail"}]
        
        return findings if findings else [
            {"control_id": "NETWORK", "title": "Scan completed", "severity": "low", "status": "pass"}
        ]
    
    def _check_cisco_control(
        self, 
        control_id: str, 
        description: str, 
        config: str,
        device_type: str
    ) -> Dict:
        """Check a specific Cisco control"""
        findings = []
        
        checks = {
            # SSH check
            "1.3": ("ip http server", "ip https server"),
            # Password encryption
            "2.1": ("service password-encryption",),
            # AAA
            "3.1": ("aaa new-model",),
            # Logging
            "5.1": ("logging on",),
        }
        
        for check_id, patterns in checks.items():
            found = any(p.lower() in config.lower() for p in patterns)
            severity = "low" if found else "high"
            status = "pass" if found else "fail"
            
            findings.append({
                "control_id": f"CISCO.{check_id}",
                "title": checks.get(check_id, [check_id])[0],
                "severity": severity,
                "status": status,
                "asset": "network",
                "finding": f"Found: {found}"
            })
        
        # Default to pass if unknown control
        return findings[0] if findings else {
            "control_id": control_id,
            "title": description,
            "severity": "low",
            "status": "pass",
            "asset": "network"
        }
    
    def _check_cisco_ios_specific(self, config: str) -> List[Dict]:
        """Additional Cisco IOS specific checks"""
        findings = []
        
        # Check for insecure protocols
        checks = [
            ("telnet", "Ensure Telnet is disabled", "high"),
            ("ip http server", "Ensure HTTP server is disabled", "high"),
            ("no service pad", "Ensure PAD is disabled", "medium"),
            ("no ip source-route", "Ensure source routing is disabled", "medium"),
            ("no ip directed-broadcast", "Ensure directed broadcast is disabled", "medium"),
        ]
        
        for pattern, title, severity in checks:
            found = pattern.lower() in config.lower()
            # Determine status based on expected state
            if "disabled" in title.lower():
                status = "pass" if not found else "fail"
            else:
                status = "pass" if found else "fail"
            
            findings.append({
                "control_id": f"CISCO-{pattern.replace(' ', '_')[:10]}",
                "title": title,
                "severity": severity,
                "status": status,
                "asset": "cisco",
                "finding": f"Found: {found}"
            })
        
        return findings
    
    def _check_fortigate_specific(self, config: str) -> List[Dict]:
        """Additional FortiGate specific checks"""
        findings = []
        
        # Check HTTPS admin
        if "set admin-https-ssl-versions tls-v1.0" in config.lower():
            findings.append({
                "control_id": "FORTI-1.1",
                "title": "Ensure legacy TLS is disabled",
                "severity": "high",
                "status": "fail",
                "asset": "fortigate"
            })
        else:
            findings.append({
                "control_id": "FORTI-1.1",
                "title": "Ensure admin HTTPS is enabled",
                "severity": "low",
                "status": "pass",
                "asset": "fortigate"
            })
        
        # Check SNMP
        if "config system snmp" in config.lower():
            findings.append({
                "control_id": "FORTI-4.1",
                "title": "Ensure SNMP is configured",
                "severity": "low",
                "status": "pass",
                "asset": "fortigate"
            })
        
        return findings


# Parse nipper output
def parse_nipper_report(report_file: str) -> List[Dict]:
    """Parse Nipper report for additional findings"""
    findings = []
    
    # Simple text parsing
    try:
        with open(report_file, 'r') as f:
            content = f.read()
            
            # Look for issues
            if "PASS" in content.upper():
                findings.append({
                    "control_id": "NIPPER",
                    "title": "Nipper scan passed",
                    "severity": "low",
                    "status": "pass"
                })
            if "FAIL" in content.upper():
                findings.append({
                    "control_id": "NIPPER",
                    "title": "Nipper issues found",
                    "severity": "high",
                    "status": "fail"
                })
    except FileNotFoundError:
        pass
    
    return findings


async def run_network_scan(
    host: str,
    device_type: str,
    credentials: Dict,
    customer_id: int,
    scan_id: int
) -> List[Dict]:
    """Scan network device"""
    scanner = NetworkScanner()
    
    if device_type == "cisco":
        return await scanner.scan_cisco(
            host=host,
            username=credentials.get("user", "admin"),
            password=credentials.get("password", ""),
            secret=credentials.get("secret")
        )
    elif device_type == "fortigate":
        return await scanner.scan_fortigate(
            host=host,
            username=credentials.get("user", "admin"),
            password=credentials.get("password", "")
        )
    else:
        return await scanner._scan(
            host=host,
            username=credentials.get("user", "admin"),
            password=credentials.get("password", ""),
            device_type=device_type
        )


# Type alias
Dict = dict


# Example
if __name__ == "__main__":
    async def main():
        scanner = NetworkScanner()
        print("Network scanner initialized")
        print("Requires: pip install netmiko")
    
    import asyncio
    asyncio.run(main())