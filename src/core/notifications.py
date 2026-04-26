"""
Notification System - Email Queue and Delivery
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import asyncio
from datetime import datetime
import jinja2


class NotificationService:
    """Email notification service"""
    
    def __init__(self, db_pool=None):
        self.db = db_pool
        self.smtp_host = None
        self.smtp_port = 587
        self.smtp_user = None
        self.smtp_password = None
        self.from_address = None
    
    def configure(
        self,
        smtp_host: str,
        smtp_port: int = 587,
        smtp_user: str = None,
        smtp_password: str = None,
        from_address: str = None
    ):
        """Configure SMTP settings"""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_address = from_address or smtp_user
    
    async def queue_notification(
        self,
        user_id: int,
        event_type: str,
        payload: Dict,
        priority: str = "medium"
    ):
        """Queue a notification"""
        if not self.db:
            return
        
        async with self.db.acquire() as conn:
            await conn.execute("""
                INSERT INTO notifications (user_id, event_type, payload, priority)
                VALUES ($1, $2, $3, $4)
            """, user_id, event_type, payload, priority)
    
    async def process_queue(self, batch_size: int = 50):
        """Process queued notifications"""
        if not self.db:
            return
        
        async with self.db.acquire() as conn:
            # Get pending notifications for users who have notifications enabled
            rows = await conn.fetch("""
                SELECT n.id, n.user_id, n.event_type, n.payload, n.priority, u.email, u.full_name
                FROM notifications n
                JOIN users u ON u.id = n.user_id
                WHERE n.status = 'pending'
                AND (SELECT enabled FROM notification_preferences 
                     WHERE user_id = n.user_id AND event_type = n.event_type) IS NOT FALSE
                ORDER BY 
                    CASE n.priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        WHEN 'low' THEN 3 
                    END,
                    n.created_at ASC
                LIMIT $1
            """, batch_size)
            
            for row in rows:
                try:
                    # Get email template
                    template = await conn.fetchrow("""
                        SELECT subject, body_text, body_html
                        FROM email_templates
                        WHERE event_type = $1
                    """, row["event_type"])
                    
                    if template:
                        # Render template
                        subject = self._render_template(
                            template["subject"], 
                            row["payload"]
                        )
                        body = self._render_template(
                            template["body_text"],
                            row["payload"]
                        )
                        
                        # Send email
                        await self._send_email(
                            row["email"],
                            subject,
                            body
                        )
                        
                        # Mark as sent
                        await conn.execute("""
                            UPDATE notifications 
                            SET status = 'sent', sent_at = NOW() 
                            WHERE id = $1
                        """, row["id"])
                except Exception as e:
                    # Mark as failed
                    await conn.execute("""
                        UPDATE notifications 
                        SET status = 'failed' 
                        WHERE id = $1
                    """, row["id"])
    
    def _render_template(self, template: str, context: Dict) -> str:
        """Render template with context"""
        # Simple template rendering
        result = template
        for key, value in context.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    async def _send_email(
        self,
        to_address: str,
        subject: str,
        body: str
    ):
        """Send email via SMTP"""
        if not self.smtp_host:
            return
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_address
        msg["To"] = to_address
        
        # Add plain text part
        msg.attach(MIMEText(body, "plain"))
        
        # Connect and send
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)


# Event helpers

async def notify_scan_complete(db_pool, customer_id: int, scan_id: int, findings_count: int):
    """Notify that scan completed"""
    from .database.schema import get_customer_name
    
    customer_name = await get_customer_name(db_pool, customer_id)
    
    # Get customer users
    async with db_pool.acquire() as conn:
        users = await conn.fetch("""
            SELECT u.id FROM users u
            JOIN customer_access ca ON ca.user_id = u.id
            WHERE ca.customer_id = $1
        """, customer_id)
        
        for user in users:
            service = NotificationService(db_pool)
            await service.queue_notification(
                user_id=user["id"],
                event_type="scan_completed",
                payload={
                    "customer_name": customer_name,
                    "finding_count": findings_count,
                    "scan_id": scan_id
                },
                priority="low"
            )


async def notify_critical_finding(db_pool, finding_id: int):
    """Notify about critical finding"""
    async with db_pool.acquire() as conn:
        finding = await conn.fetchrow("""
            SELECT f.*, c.name as customer_name
            FROM findings f
            JOIN customers c ON c.id = f.customer_id
            WHERE f.id = $1
        """, finding_id)
        
        if finding and finding.get("severity") in ("critical", "high"):
            users = await conn.fetch("""
                SELECT u.id FROM users u
                JOIN customer_access ca ON ca.user_id = u.id
                WHERE ca.customer_id = $1
            """, finding["customer_id"])
            
            service = NotificationService(db_pool)
            for user in users:
                await service.queue_notification(
                    user_id=user["id"],
                    event_type="finding_critical",
                    payload={
                        "customer_name": finding["customer_name"],
                        "control_id": finding["control_id"],
                        "finding_title": finding["title"],
                        "asset": finding["asset"],
                        "severity": finding["severity"],
                        "remediation": finding.get("remediation", "")
                    },
                    priority="high"
                )


async def notify_scan_failed(db_pool, customer_id: int, scan_id: int, error: str):
    """Notify that scan failed"""
    async with db_pool.acquire() as conn:
        customer = await conn.fetchrow("""
            SELECT name FROM customers WHERE id = $1
        """, customer_id)
        
        users = await conn.fetch("""
            SELECT u.id FROM users u
            JOIN customer_access ca ON ca.user_id = u.id
            WHERE ca.customer_id = $1
        """, customer_id)
        
        service = NotificationService(db_pool)
        for user in users:
            await service.queue_notification(
                user_id=user["id"],
                event_type="scan_failed",
                payload={
                    "customer_name": customer["name"] if customer else "Unknown",
                    "scan_id": scan_id,
                    "error": error
                },
                priority="high"
            )


# Example
if __name__ == "__main__":
    print("Notification service ready")
    print("Configure with SMTP settings via .env")