"""
Multi-Cloud Scanner Module
"""
from .azure import AzureScanner, run_azure_scan
from .gcp import GCPScanner, run_gcp_scan

__all__ = [
    "AzureScanner",
    "run_azure_scan",
    "GCPScanner",
    "run_gcp_scan",
]