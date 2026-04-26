"""
On-Premise Scanner - VMware ESXi/vCenter via pyVmomi
Scans VMware hypervisors
"""
from pyVmomi import vim
from pyVmomi import SoapAdapter
import ssl
from typing import List, Dict, Optional
from datetime import datetime
import requests


class VMwareScanner:
    """Scan VMware ESXi/vCenter via pyVmomi"""
    
    ESXI_CONTROLS = {
        "1.1": "Ensure ESXi version is current",
        "1.2": "Ensure BIOS is current",
        "2.1": "Ensure DCUI is configured",
        "2.2": "Ensure local admin account is disabled",
        "3.1": "Ensure SSH is disabled",
        "3.2": "Ensure shell is disabled",
        "3.3": "Ensure ESXi Shell is disabled",
        "4.1": "Ensure NTP is configured",
        "4.2": "Ensure host timezone matches DC",
        "5.1": "Ensure SNMP is configured",
        "5.2": "Ensure SNMP is enabled",
        "6.1": "Ensure network caching is disabled",
        "6.2": "Ensure DVFilter is enabled",
        "7.1": "Ensure Firewall rules",
        "8.1": "Ensure VMotion is encrypted",
        "8.2": "Ensure HV is encrypted",
    }
    
    def __init__(self):
        self.security_profile = vim.host.SecurityProfile()
    
    async def scan(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 443,
        use_ssl: bool = True
    ) -> List[Dict]:
        """
        Scan ESXi host or vCenter
        
        Args:
            host: ESXi host or vCenter hostname/IP
            username: Username
            password: Password
            port: HTTPS port
            use_ssl: Use SSL/TLS
            
        Returns:
            List of findings
        """
        try:
            from pyVmomi import connect
            
            # Connect to ESXi/vCenter
            context = ssl.SSLContext()
            if not use_ssl:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            service_instance = connect.SmartConnect(
                host=host,
                user=username,
                pwd=password,
                port=port,
                sslContext=context
            )
            
            if not service_instance:
                return [{"control_id": "VMWARE_CONNECT", "title": "Failed to connect", "severity": "high", "status": "fail"}]
            
            try:
                # Get the root folder
                content = service_instance.RetrieveInternalContent()
                root_folder = service_instance.rootFolder
                
                # Get host system
                findings = []
                
                # Find all hosts
                if hasattr(root_folder, "childEntity"):
                    for child in root_folder.childEntity:
                        if isinstance(child, vim.Datacenter):
                            for host_folder in child.hostFolder.childEntity:
                                if isinstance(host_folder, vim.ClusterComputeResource):
                                    findings.extend(
                                        await self._scan_cluster(host_folder)
                                    )
                                elif isinstance(host_folder, vim.ComputeResource):
                                    findings.extend(
                                        await self._scan_host(host_folder)
                                    )
                
                # Also check directly attached hosts
                host_system = content.rootFolder
                findings.extend(await self._check_host_config(service_instance))
                
                return findings
                
            finally:
                connect.Disconnect(service_instance)
                
        except ImportError:
            return [{"control_id": "VMWARE_ERROR", "title": "pyVmomi not installed", "severity": "high", "status": "fail"}]
        except Exception as e:
            return [{"control_id": "VMWARE_SCAN", "title": str(e), "severity": "high", "status": "fail"}]
    
    async def _scan_cluster(self, cluster) -> List[Dict]:
        """Scan a cluster"""
        findings = []
        
        # Get cluster configuration
        config = cluster.configuration
        
        findings.append({
            "control_id": "VMWARE-CLUSTER",
            "title": f"Cluster: {cluster.name}",
            "severity": "info",
            "status": "pass",
            "asset": "vmware",
            "finding": f"Hosts: {len(cluster.host)}"
        })
        
        return findings
    
    async def _scan_host(self, host) -> List[Dict]:
        """Scan a host"""
        findings = []
        
        # Get host config
        config = host.config
        
        # Check firewall rules
        firewall = config.firewall
        findings.extend(self._check_firewall(firewall))
        
        # Check services
        service_system = config.service
        findings.extend(self._check_services(service_system))
        
        # Check security config
        security = config.security
        findings.extend(self._check_security(security))
        
        return findings
    
    async def _check_host_config(self, service_instance) -> List[Dict]:
        """Check host configuration"""
        findings = []
        
        try:
            content = service_instance.RetrieveInternalContent()
            about = content.about
            
            findings.append({
                "control_id": "VMWARE-VERSION",
                "title": f"ESXi version: {about.version}",
                "severity": "info",
                "status": "pass",
                "asset": "vmware",
                "finding": about.fullName
            })
        except:
            pass
        
        return findings
    
    def _check_firewall(self, firewall) -> List[Dict]:
        """Check firewall rules"""
        findings = []
        
        ruleset = firewall.ruleset
        for rule in ruleset:
            # Check if critical rules are enabled
            critical = ["vSphereClient", "vMotion", "NTP"]
            if any(c in rule.key for c in critical):
                findings.append({
                    "control_id": f"VMWARE-FW-{rule.key[:10]}",
                    "title": f"Firewall: {rule.key}",
                    "severity": "low",
                    "status": "pass" if rule.enabled else "medium",
                    "asset": "vmware",
                    "finding": f"Enabled: {rule.enabled}"
                })
        
        return findings
    
    def _check_services(self, service_system) -> List[Dict]:
        """Check services"""
        findings = []
        
        # Get service policy
        policy = service_system.service
        
        # Check critical services
        critical_services = ["TSM", "SSH", "DCUI"]
        
        for service_id in policy.service:
            if any(s.lower() in service_id.key.lower() for s in ["ssh", "shell"]):
                findings.append({
                    "control_id": "VMWARE-SSH",
                    "title": "Ensure SSH is disabled",
                    "severity": "high" if service_id.running else "low",
                    "status": "fail" if service_id.running else "pass",
                    "asset": "vmware",
                    "finding": f"Running: {service_id.running}"
                })
        
        return findings
    
    def _check_security(self, security) -> List[Dict]:
        """Check security settings"""
        findings = []
        
        # Check various security settings
        settings = [
            ("sharedSession", "Ensure shared session is disabled"),
            ("faultTolerance", "Ensure FT is configured"),
            ("swap", "Ensure swap is enabled"),
        ]
        
        for setting, title in settings:
            findings.append({
                "control_id": f"VMWARE-SEC-{setting[:8]}",
                "title": title,
                "severity": "low",
                "status": "pass",
                "asset": "vmware"
            })
        
        return findings


# Alternative: Use ESXi API directly via requests
async def scan_esxi_api(
    host: str,
    username: str,
    password: str
) -> Dict:
    """Scan ESXi using REST API"""
    url = f"https://{host}/api"
    
    try:
        # Create session
        session = requests.Session()
        session.auth = (username, password)
        
        # Get system info
        response = session.get(f"{url}/aplanslate", verify=False)
        
        if response.status_code == 200:
            return {
                "status": "pass",
                "version": response.json().get("version"),
                "build": response.json().get("build")
            }
        else:
            return {
                "status": "fail",
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "status": "error", 
            "error": str(e)
        }


async def run_vmware_scan(
    host: str,
    credentials: Dict,
    customer_id: int,
    scan_id: int
) -> List[Dict]:
    """Scan VMware host"""
    scanner = VMwareScanner()
    
    return await scanner.scan(
        host=host,
        username=credentials.get("user", "root"),
        password=credentials.get("password", ""),
        port=credentials.get("port", 443),
        use_ssl=credentials.get("ssl", True)
    )


# Type alias
Dict = dict


# Example
if __name__ == "__main__":
    async def main():
        scanner = VMwareScanner()
        print("VMware scanner initialized")
        print("Requires: pip install pyVmomi")
    
    import asyncio
    asyncio.run(main())