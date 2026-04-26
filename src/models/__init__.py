# Shared data models
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FindingStatus(str, Enum):
    OPEN = "open"
    FIXED = "fixed"
    ACCEPTED = "accepted"


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


@dataclass
class Finding:
    id: Optional[int]
    scan_id: int
    customer_id: int
    control_id: str
    title: str
    description: str
    severity: Severity
    status: FindingStatus
    asset: str
    remediation: str
    created_at: datetime


@dataclass
class Scan:
    id: Optional[int]
    customer_id: int
    scan_type: str
    status: ScanStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    findings_count: int
    error_message: Optional[str]
    created_by: int


@dataclass
class User:
    id: Optional[int]
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    mfa_enabled: bool
    mfa_secret_encrypted: Optional[str]
    failed_attempts: int
    locked_until: Optional[datetime]
    last_login: Optional[datetime]


@dataclass
class Customer:
    id: Optional[int]
    name: str
    type: str  # aws, onprem, hybrid
    status: str  # active, inactive