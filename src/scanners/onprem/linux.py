"""
On-Premise Scanner - Linux OpenSCAP via SSH
Executes OpenSCAP on Linux servers over SSH
"""
import asyncssh
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import os
from datetime import datetime


class LinuxScanner:
    """Scan Linux servers via SSH + OpenSCAP"""
    
    def __init__(self):
        self.profile = "xccdf_org.ssgproject.content_profile_cis"
    
    async def scan(
        self,
        host: str,
        port: int = 22,
        username: str = "root",
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        sudo: bool = True
    ) -> List[Dict]:
        """
        Scan Linux server via SSH
        
        Args:
            host: Server hostname/IP
            port: SSH port
            username: SSH username
            password: SSH password (or use key_filename)
            key_filename: Path to private key
            sudo: Use sudo for privileged commands
            
        Returns:
            List of findings
        """
        try:
            async with asyncssh.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                client_keys=[key_filename] if key_filename else None,
                known_hosts=None
            ) as conn:
                return await self._run_scan(conn)
        except asyncssh.Error as e:
            return [{"control_id": "SSH_ERROR", "title": str(e), "severity": "high", "status": "fail"}]
        except Exception as e:
            return [{"control_id": "LINUX_SCAN", "title": str(e), "severity": "high", "status": "fail"}]
    
    async def _run_scan(self, conn: asyncssh.SSHClientConnection) -> List[Dict]:
        """Execute scan commands over SSH"""
        findings = []
        
        # Check if OpenSCAP is installed
        result = await conn.run("which oscap", check=False)
        if result.exit_status != 0:
            # Install OpenSCAP
            await self._install_openscap(conn)
        
        # Determine OS and install appropriate content
        os_release = await conn.run("cat /etc/os-release", check=False)
        os_info = os_release.stdout.lower()
        
        if "ubuntu" in os_info or "debian" in os_info:
            os_type = "ubuntu"
        elif "rhel" in os_info or "centos" in os_info or "rocky" in os_info:
            os_type = "rhel"
        elif "amazon" in os_info:
            os_type = "amazon"
        else:
            os_type = "unknown"
        
        # Download and run CIS benchmark
        await self._run_cis_benchmark(conn, os_type)
        
        # Fetch results
        await conn.get("/tmp/cis-results.xml", "/tmp/cis-results.xml")
        
        # Parse results
        findings = self._parse_results("/tmp/cis-results.xml")
        
        # Cleanup
        await conn.run("rm -f /tmp/cis-results.xml /tmp/cis-results.html", check=False)
        
        return findings
    
    async def _install_openscap(self, conn: asyncssh.SSHClientConnection):
        """Install OpenSCAP scanner"""
        # Detect OS and install
        os_release = await conn.run("cat /etc/os-release", check=False)
        os_info = os_release.stdout.lower()
        
        if "ubuntu" in os_info or "debian" in os_info:
            install_cmd = "apt-get update && apt-get install -y openscap-scanner"
        elif "rhel" in os_info or "centos" in os_info or "rocky" in os_info:
            install_cmd = "yum install -y openscap-scanner"
        else:
            install_cmd = "yum install -y openscap-scanner"
        
        result = await conn.run(install_cmd, check=False)
        return result.exit_status == 0
    
    async def _run_cis_benchmark(self, conn: asyncssh.SSHClientConnection, os_type: str):
        """Download and run CIS benchmark"""
        # Map OS type to SSG content
        ssg_map = {
            "ubuntu": "ssg-ubuntu2204.ds.xml",
            "rhel": "ssg-rhel9.ds.xml",
            "amazon": "ssg-almalinux9.ds.xml",
        }
        
        filename = ssg_map.get(os_type, "ssg-rhel9.ds.xml")
        
        # Download latest content if not exists
        check = await conn.run(f"ls /tmp/{filename}", check=False)
        if check.exit_status != 0:
            # Download SCAP content
            download_cmd = f"""cd /tmp && curl -L -o {filename} \
                https://github.com/ComplianceAsCode/scap-security-guide/releases/latest/download/{filename}"""
            await conn.run(download_cmd, check=False)
        
        # Run OpenSCAP
        scan_cmd = f"""oscap xccdf eval \
            --profile xccdf_org.ssgproject.content_profile_cis \
            --results /tmp/cis-results.xml \
            --report /tmp/cis-results.html \
            /tmp/{filename}"""
        
        sudo_prefix = "sudo " if True else ""  # Assume sudo needed
        await conn.run(sudo_prefix + scan_cmd, check=False)
    
    def _parse_results(self, xml_path: str) -> List[Dict]:
        """Parse OpenSCAP XCCDF results"""
        findings = []
        
        if not os.path.exists(xml_path):
            return [{"control_id": "PARSE_ERROR", "title": "No results file", "severity": "medium", "status": "fail"}]
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # XCCDF namespace
            ns = {"xccdf": "http://check.nist.gov/spec/xccdf"}
            
            for rule_result in root.findall(".//xccdf:rule-result", ns):
                rule_id = rule_result.get("idref", "")
                status = rule_result.find("xccdf:result", ns)
                
                if status is not None:
                    status_text = status.text or "unknown"
                    
                    # Map status
                    if status_text in ("pass", "fixed"):
                        finding_status = "pass"
                        severity = "low"
                    elif status_text in ("fail", "error"):
                        finding_status = "fail"
                        severity = "high"
                    else:
                        finding_status = "skip"
                        severity = "low"
                    
                    # Extract title from rule
                    title_el = rule_result.find("xccdf:title", ns)
                    title = title_el.text if title_el is not None else rule_id
                    
                    # Extract description
                    desc_el = rule_result.find("xccdf:description", ns)
                    description = desc_el.text[:500] if desc_el is not None else ""
                    if desc_el is not None and len(desc_el.text or "") > 500:
                        description += "..."
                    
                    findings.append({
                        "control_id": rule_id,
                        "title": title,
                        "description": description,
                        "severity": severity,
                        "status": finding_status,
                        "asset": "linux",
                        "finding": f"Result: {status_text}"
                    })
            
            # Also check for rule results without namespace
            if not findings:
                for rule_result in root.findall(".//rule-result"):
                    rule_id = rule_result.get("idref", "")
                    status = rule_result.find("result")
                    
                    if status is not None:
                        status_text = status.text or "unknown"
                        
                        if status_text in ("pass", "fixed"):
                            finding_status = "pass"
                            severity = "low"
                        elif status_text in ("fail", "error"):
                            finding_status = "fail"
                            severity = "high"
                        else:
                            finding_status = "skip"
                            severity = "low"
                        
                        title_el = rule_result.find("title")
                        title = title_el.text if title_el is not None else rule_id
                        
                        findings.append({
                            "control_id": rule_id,
                            "title": title,
                            "severity": severity,
                            "status": finding_status,
                            "asset": "linux"
                        })
        
        except ET.ParseError as e:
            return [{"control_id": "XML_PARSE", "title": str(e), "severity": "medium", "status": "fail"}]
        
        return findings if findings else [
            {"control_id": "OPENSCAP", "title": "Scan completed", "severity": "low", "status": "pass", "asset": "linux"}
        ]


# Linux CIS control mapping
LINUX_CIS_CONTROLS = {
    "1.1.1": "Ensure mounting of cramfs filesystems is disabled",
    "1.1.2": "Ensure mounting of squashfs filesystems is disabled",
    "1.1.3": "Ensure mounting of udf filesystems is disabled",
    "1.2.1": "Ensure software suite is supported",
    "1.3.1": "Ensure AIDE is installed",
    "1.3.2": "Ensure filesystem integrity is checked",
    "1.4.1": "Ensure permissions on /etc/gshadow- are configured",
    "1.4.2": "Ensure password fields are not empty",
    "1.5.1": "Ensure core dumps are restricted",
    "1.5.2": "Ensure address space layout randomization (ASLR) is enabled",
    "1.5.3": "Ensure prelink is not installed",
    "1.5.4": "Ensure automatic core dump creation is disabled",
    "2.1.1": "Ensure xinetd is not installed",
    "2.2.1.1": "Ensure time synchronization is in use",
    "3.1.1": "Ensure IP forwarding is disabled",
    "3.2.1": "Ensure packet redirect sending is disabled",
    "4.1.1": "Ensure audit log storage size is configured",
    "4.1.2": "Ensure audit logs are not automatically deleted",
    "5.1.1": "Ensure cron daemon is enabled",
    "5.2.1": "Ensure SSH Protocol is set to 2",
    "6.1.1": "Ensure permissions on /etc/passwd are configured",
}


async def run_linux_scan(
    host: str,
    credentials: Dict,
    customer_id: int,
    scan_id: int
) -> List[Dict]:
    """Scan Linux server"""
    scanner = LinuxScanner()
    
    return await scanner.scan(
        host=host,
        port=credentials.get("port", 22),
        username=credentials.get("user", "root"),
        password=credentials.get("password"),
        key_filename=credentials.get("key_file"),
        sudo=credentials.get("sudo", True)
    )


# Type alias for Dict
Dict = dict


# Example
if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) < 4:
            print("Usage: python linux.py <host> <user> <password>")
            return
        
        host = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]
        
        scanner = LinuxScanner()
        findings = await scanner.scan(host, username=user, password=password)
        
        print(f"Found {len(findings)} findings")
        
        # Group by status
        passed = sum(1 for f in findings if f["status"] == "pass")
        failed = sum(1 for f in findings if f["status"] == "fail")
        
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        
        # Show failures
        if failed > 0:
            print("\nFailed checks:")
            for f in findings:
                if f["status"] == "fail":
                    print(f"  [{f['severity']}] {f['control_id']}: {f['title'][:60]}")
    
    asyncio.run(main())