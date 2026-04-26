"""
Scheduler - APScheduler Integration
Manages scan scheduling
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict, List, Callable, Optional
from datetime import datetime
import asyncio


class ScanScheduler:
    """Scan scheduler using APScheduler"""
    
    def __init__(self, db_pool=None):
        self.scheduler = AsyncIOScheduler()
        self.db = db_pool
        self.jobs = {}
    
    def start(self):
        """Start scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
    
    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
    
    def add_scan_job(
        self,
        job_id: str,
        customer_id: int,
        scan_type: str,
        schedule_type: str,
        cron_expression: Optional[str] = None,
        interval_hours: Optional[int] = None
    ) -> str:
        """
        Add a scan job
        
        Args:
            job_id: Unique job ID
            customer_id: Customer ID
            scan_type: Type of scan (aws, linux, windows, etc)
            schedule_type: daily, weekly, monthly, or custom
            cron_expression: Cron expression for custom schedule
            interval_hours: Hours between scans for interval
            
        Returns:
            Job ID
        """
        # Map schedule type to trigger
        if schedule_type == "daily":
            trigger = IntervalTrigger(hours=24)
        elif schedule_type == "weekly":
            trigger = IntervalTrigger(hours=168)  # 7 days
        elif schedule_type == "monthly":
            trigger = IntervalTrigger(hours=720)  # ~30 days
        elif schedule_type == "custom" and cron_expression:
            trigger = CronTrigger.from_cron(cron_expression)
        elif interval_hours:
            trigger = IntervalTrigger(hours=interval_hours)
        else:
            trigger = IntervalTrigger(hours=24)  # Default to daily
        
        # Add job
        job = self.scheduler.add_job(
            self._run_scan,
            trigger=trigger,
            args=[customer_id, scan_type],
            id=job_id,
            replace_existing=True
        )
        
        self.jobs[job_id] = {
            "customer_id": customer_id,
            "scan_type": scan_type,
            "schedule_type": schedule_type
        }
        
        return job.id
    
    def remove_job(self, job_id: str):
        """Remove a job"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
        except Exception:
            pass
    
    def get_jobs(self) -> List[Dict]:
        """Get all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "next_run": str(job.next_run) if job.next_run else None,
                "trigger": str(job.trigger)
            })
        return jobs
    
    async def _run_scan(self, customer_id: int, scan_type: str):
        """Execute a scheduled scan"""
        # This would integrate with the scan engine
        # For now, just log
        print(f"Running scheduled scan for customer {customer_id}, type {scan_type}")
        
        # Update last_run in database
        if self.db:
            async with self.db.acquire() as conn:
                await conn.execute("""
                    UPDATE scan_schedules 
                    SET last_run = NOW() 
                    WHERE customer_id = $1
                """, customer_id)
    
    def list_jobs(self) -> Dict:
        """List all jobs with their details"""
        return self.jobs.copy()


# Singleton instance
scheduler = None


def get_scheduler(db_pool=None) -> ScanScheduler:
    """Get scheduler singleton"""
    global scheduler
    if scheduler is None:
        scheduler = ScanScheduler(db_pool)
    return scheduler


# Cron expression examples
SCHEDULE_PRESETS = {
    "daily": "0 2 * * *",  # 2 AM daily
    "weekly": "0 2 * * 0",  # 2 AM Sundays
    "monthly": "0 2 1 * *",  # 2 AM 1st of month
    "quarterly": "0 2 1 1,4,7,10 * *",  # Quarterly
}


# Example usage
if __name__ == "__main__":
    import sys
    
    async def main():
        scheduler = ScanScheduler()
        scheduler.start()
        
        # Add a daily scan job
        job_id = scheduler.add_scan_job(
            job_id="customer-1-daily",
            customer_id=1,
            scan_type="aws",
            schedule_type="daily"
        )
        
        print(f"Added job: {job_id}")
        
        # List jobs
        jobs = scheduler.get_jobs()
        print(f"Scheduled jobs: {jobs}")
        
        # Wait for a bit
        await asyncio.sleep(5)
        
        scheduler.stop()
    
    asyncio.run(main())