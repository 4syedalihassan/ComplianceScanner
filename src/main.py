"""
Compliance Scanner - REST API Server
FastAPI application with all endpoints
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import Optional
import asyncpg
import os
import subprocess
import threading
import time

from auth.mfa import AuthService, decode_token
from models import User, Customer, Scan, Finding


# Database pool
DB_POOL: Optional[asyncpg.Pool] = None

# Frontend process
frontend_process: Optional[subprocess.Popen] = None


def get_frontend_path():
    """Get the path to the frontend build"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "frontend-next", ".next")


async def start_frontend():
    """Start the frontend dev server in background"""
    global frontend_process
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, "frontend-next")
    
    # Check if build exists
    frontend_path = get_frontend_path()
    if not os.path.exists(frontend_path):
        print("Frontend not built. Building...")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=frontend_dir,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Frontend build failed: {result.stderr}")
            return False
    
    # Start frontend dev server
    try:
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        print("Frontend dev server started on http://localhost:3000")
        return True
    except Exception as e:
        print(f"Failed to start frontend: {e}")
        return False


def stop_frontend():
    """Stop the frontend process"""
    global frontend_process
    if frontend_process:
        frontend_process.terminate()
        frontend_process.wait()
        print("Frontend process stopped")


def get_db():
    """Get database pool"""
    return DB_POOL


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    global DB_POOL
    
    # Connect to database
    try:
        DB_POOL = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            database=os.getenv("DB_NAME", "compliance")
        )
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
        print("Running in demo mode without database")
    
    # Start frontend in background
    if os.getenv("START_FRONTEND", "true").lower() == "true":
        threading.Thread(target=start_frontend, daemon=True).start()
        # Give frontend time to start
        time.sleep(3)
    
    yield
    
    # Cleanup
    stop_frontend()
    if DB_POOL:
        await DB_POOL.close()


app = FastAPI(
    title="Compliance Scanner",
    description="CIS Benchmark scanning and compliance platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = decode_token(credentials.credentials)
        return payload
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication"
        )


# =====================
# AUTH ROUTES
# =====================

@app.post("/auth/login")
async def login(email: str, password: str):
    """Login with email/password"""
    auth_service = AuthService(DB_POOL)
    return await auth_service.authenticate(email, password)


@app.post("/auth/mfa-verify")
async def verify_mfa(temp_token: str, code: str):
    """Verify MFA code"""
    auth_service = AuthService(DB_POOL)
    return await auth_service.verify_mfa(temp_token, code)


@app.post("/auth/mfa-setup")
async def setup_mfa(current_user: dict = Depends(get_current_user)):
    """Setup MFA for user"""
    auth_service = AuthService(DB_POOL)
    return await auth_service.setup_mfa(current_user["user_id"])


@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    # Implementation here
    pass


@app.post("/auth/logout")
async def logout():
    """Logout"""
    return {"message": "Logged out"}


# =====================
# CUSTOMER ROUTES
# =====================

@app.get("/api/customers")
async def list_customers(
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """List customers"""
    async with db.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.*, 
                (SELECT COUNT(*) FROM aws_accounts WHERE customer_id = c.id) as aws_accounts,
                (SELECT COUNT(*) FROM onprem_environments WHERE customer_id = c.id) as onprem_envs
            FROM customers c
            WHERE status = 'active'
        """)
        return [dict(r) for r in rows]


@app.post("/api/customers")
async def create_customer(
    name: str,
    type: str,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Create customer"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    async with db.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO customers (name, type)
            VALUES ($1, $2)
            RETURNING *
        """, name, type)
        return dict(row)


@app.get("/api/customers/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get customer details"""
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM customers WHERE id = $1", customer_id)
        if not row:
            raise HTTPException(status_code=404, detail="Customer not found")
        return dict(row)


# =====================
# SCAN ROUTES
# =====================

@app.post("/api/customers/{customer_id}/scan")
async def trigger_scan(
    customer_id: int,
    scan_types: list[str],
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Trigger scan for customer"""
    if current_user.get("role") not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Operator+ only")
    
    async with db.acquire() as conn:
        # Create scan record
        scan = await conn.fetchrow("""
            INSERT INTO scans (customer_id, scan_type, status, created_by)
            VALUES ($1, $2, 'pending', $3)
            RETURNING *
        """, customer_id, ",".join(scan_types), current_user["user_id"])
        
        # TODO: Trigger scan engine asynchronously
        # For now, return scan record
        return dict(scan)


@app.get("/api/customers/{customer_id}/scans")
async def list_scans(
    customer_id: int,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """List scans for customer"""
    async with db.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM scans 
            WHERE customer_id = $1
            ORDER BY created_at DESC
            LIMIT 50
        """, customer_id)
        return [dict(r) for r in rows]


@app.get("/api/scans/{scan_id}")
async def get_scan(
    scan_id: int,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get scan details"""
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM scans WHERE id = $1", scan_id)
        if not row:
            raise HTTPException(status_code=404, detail="Scan not found")
        return dict(row)


# =====================
# FINDING ROUTES
# =====================

@app.get("/api/customers/{customer_id}/findings")
async def list_findings(
    customer_id: int,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """List findings for customer"""
    async with db.acquire() as conn:
        query = "SELECT * FROM findings WHERE customer_id = $1"
        params = [customer_id]
        
        if severity:
            query += " AND severity = $2"
            params.append(severity)
        if status:
            query += f" AND status = ${len(params)+1}"
            params.append(status)
        
        query += f" ORDER BY created_at DESC LIMIT ${len(params)+1}"
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        return [dict(r) for r in rows]


@app.get("/api/findings/{finding_id}")
async def get_finding(
    finding_id: int,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Get finding details"""
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM findings WHERE id = $1", finding_id)
        if not row:
            raise HTTPException(status_code=404, detail="Finding not found")
        return dict(row)


@app.put("/api/findings/{finding_id}/status")
async def update_finding_status(
    finding_id: int,
    status: str,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Update finding status"""
    if current_user.get("role") not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Operator+ only")
    
    async with db.acquire() as conn:
        await conn.execute(
            "UPDATE findings SET status = $1 WHERE id = $2",
            status, finding_id
        )
        return {"message": "Status updated"}


# =====================
# REPORT ROUTES
# =====================

@app.get("/api/customers/{customer_id}/reports")
async def list_reports(
    customer_id: int,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """List reports for customer"""
    # Implementation: list from S3
    return []


# =====================
# USER ROUTES (Admin)
# =====================

@app.get("/api/users")
async def list_users(
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """List users (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    async with db.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, email, full_name, role, mfa_enabled, last_login, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        return [dict(r) for r in rows]


@app.post("/api/users")
async def create_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "viewer",
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Create user (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    from auth.mfa import hash_password
    
    async with db.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO users (email, password_hash, full_name, role)
            VALUES ($1, $2, $3, $4)
            RETURNING id, email, full_name, role
        """, email, hash_password(password), full_name, role)
        return dict(row)


# =====================
# AWS ACCOUNT ROUTES
# =====================

@app.get("/api/customers/{customer_id}/aws-accounts")
async def list_aws_accounts(
    customer_id: int,
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """List AWS accounts for customer"""
    async with db.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM aws_accounts 
            WHERE customer_id = $1
            ORDER BY created_at DESC
        """, customer_id)
        return [dict(r) for r in rows]


@app.post("/api/customers/{customer_id}/aws-accounts")
async def add_aws_account(
    customer_id: int,
    account_id: str,
    role_arn: str,
    region: str = "us-east-1",
    current_user: dict = Depends(get_current_user),
    db: asyncpg.Pool = Depends(get_db)
):
    """Add AWS account"""
    if current_user.get("role") not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Operator+ only")
    
    async with db.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO aws_accounts (customer_id, account_id, role_arn, region)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """, customer_id, account_id, role_arn, region)
        return dict(row)


# =====================
# HEALTH CHECK
# =====================

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "api": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)