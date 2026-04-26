"""
AWS Scanner - boto3 Direct API Checks
Direct CIS AWS checks via boto3 API calls
"""
import boto3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import asyncio


class Boto3Checker:
    """Direct boto3 CIS checks"""
    
    def __init__(self, credentials: Dict):
        self.access_key = credentials["AccessKeyId"]
        self.secret_key = credentials["SecretAccessKey"]
        self.session_token = credentials.get("SessionToken")
        self.region = "us-east-1"
        
        # Create session
        session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.session_token,
            region_name=self.region
        )
        
        self.iam = session.client("iam")
        self.s3 = session.client("s3")
        self.cloudtrail = session.client("cloudtrail")
        self.config = session.client("config")
        self.ec2 = session.client("ec2")
        self.cloudwatch = session.client("cloudwatch")
        self.logs = session.client("logs")
        self.kms = session.client("kms")
    
    async def check_all(self) -> List[Dict]:
        """Run all boto3 checks"""
        checks = [
            self.check_iam_password_policy,
            self.check_iam_mfa,
            self.check_cloudtrail_enabled,
            self.check_s3_public_access,
            self.check_s3_encryption,
            self.check_cloudtrail_bucket,
            self.check_cloudwatch_logs,
            self.check_kms_key_rotation,
        ]
        
        results = []
        for check in checks:
            result = await asyncio.to_thread(check)
            results.extend(result)
        
        return results
    
    # === IAM Checks ===
    
    def check_iam_password_policy(self) -> List[Dict]:
        """CIS 1.8 - Ensure IAM password policy requires minimum length of 14 or greater"""
        try:
            policy = self.iam.get_account_password_policy()
            min_length = policy["PasswordPolicy"].get("MinimumPasswordLength", 0)
            
            return [{
                "control_id": "1.8",
                "title": "Ensure IAM password policy requires minimum length of 14 or greater",
                "severity": "high" if min_length < 14 else "low",
                "status": "fail" if min_length < 14 else "pass",
                "asset": "IAM Password Policy",
                "finding": f"Minimum password length: {min_length}"
            }]
        except self.iam.exceptions.NoSuchEntityException:
            return [{
                "control_id": "1.8",
                "title": "Ensure IAM password policy requires minimum length of 14 or greater",
                "severity": "high",
                "status": "fail",
                "asset": "IAM Password Policy",
                "finding": "No password policy configured"
            }]
        except Exception as e:
            return [{"control_id": "1.8", "title": str(e), "severity": "medium", "status": "error"}]
    
    def check_iam_mfa(self) -> List[Dict]:
        """CIS 1.9 - Ensure hardware MFA is enabled for root account"""
        try:
            # Check root account MFA
            account_summary = self.iam.get_account_summary()
            has_mfa = account_summary.get("AccountMFAEnabled", 0) == 1
            
            return [{
                "control_id": "1.9",
                "title": "Ensure hardware MFA is enabled for root account",
                "severity": "critical" if not has_mfa else "low",
                "status": "fail" if not has_mfa else "pass",
                "asset": "Root Account",
                "finding": f"MFA enabled: {has_mfa}"
            }]
        except Exception as e:
            return [{"control_id": "1.9", "title": str(e), "severity": "medium", "status": "error"}]
    
    # === Logging Checks ===
    
    def check_cloudtrail_enabled(self) -> List[Dict]:
        """CIS 2.1 - Ensure CloudTrail is enabled"""
        try:
            trails = self.cloudtrail.describe_trails()
            has_trail = len(trails.get("TraillList", [])) > 0
            
            return [{
                "control_id": "2.1",
                "title": "Ensure CloudTrail is enabled",
                "severity": "critical" if not has_trail else "low",
                "status": "fail" if not has_trail else "pass",
                "asset": "CloudTrail",
                "finding": f"Trails configured: {len(trails.get('TraillList', []))}"
            }]
        except Exception as e:
            return [{"control_id": "2.1", "title": str(e), "severity": "medium", "status": "error"}]
    
    def check_cloudtrail_bucket(self) -> List[Dict]:
        """CIS 2.2 - Ensure CloudTrail bucket is not public"""
        try:
            trails = self.cloudtrail.describe_trails()
            findings = []
            
            for trail in trails.get("TraillList", []):
                bucket_name = trail.get("S3BucketName", "Unknown")
                
                # Check bucket policy
                try:
                    policy = self.s3.get_bucket_policy(Bucket=bucket_name)
                    policy_text = policy.get("Policy", "")
                    
                    # Check for public access
                    is_public = "Principal" in policy_text and "*" in policy_text
                    
                    findings.append({
                        "control_id": "2.2",
                        "title": "Ensure CloudTrail bucket is not public",
                        "severity": "high" if is_public else "low",
                        "status": "fail" if is_public else "pass",
                        "asset": f"S3:{bucket_name}",
                        "finding": f"Public access: {is_public}"
                    })
                except self.s3.exceptions.NoSuchBucketPolicy:
                    findings.append({
                        "control_id": "2.2",
                        "title": "Ensure CloudTrail bucket is not public",
                        "severity": "low",
                        "status": "pass",
                        "asset": f"S3:{bucket_name}",
                        "finding": "No bucket policy"
                    })
            
            return findings if findings else [{
                "control_id": "2.2",
                "title": "No CloudTrail configured",
                "severity": "medium",
                "status": "fail",
                "asset": "CloudTrail"
            }]
        except Exception as e:
            return [{"control_id": "2.2", "title": str(e), "severity": "medium", "status": "error"}]
    
    def check_cloudwatch_logs(self) -> List[Dict]:
        """CIS 2.5 - Ensure CloudTrail logs are stored in CloudWatch Logs"""
        try:
            trails = self.cloudtrail.describe_trails()
            findings = []
            
            for trail in trails.get("TraillList", []):
                has_logs = bool(trail.get("CloudWatchLogsLogGroupArn"))
                
                findings.append({
                    "control_id": "2.5",
                    "title": "Ensure CloudTrail logs are stored in CloudWatch Logs",
                    "severity": "medium" if not has_logs else "low",
                    "status": "fail" if not has_logs else "pass",
                    "asset": f"CloudTrail:{trail.get('Name', trail.get('TrailName'))}",
                    "finding": f"CloudWatch Logs: {has_logs}"
                })
            
            return findings
        except Exception as e:
            return [{"control_id": "2.5", "title": str(e), "severity": "medium", "status": "error"}]
    
    # === S3 Checks ===
    
    def check_s3_public_access(self) -> List[Dict]:
        """CIS 4.1 - Ensure S3 buckets are not publicly accessible"""
        try:
            # Get all buckets
            buckets = self.s3.list_buckets()
            findings = []
            
            for bucket in buckets.get("Buckets", []):
                bucket_name = bucket["Name"]
                
                # Check block public access
                try:
                    block = self.s3.get_public_access_block(Bucket=bucket_name)
                    blocked = block.get("PublicAccessBlockConfiguration", {})
                    
                    if all(blocked.get(f, True) for f in ["BlockPublicAcls", "BlockPublicPolicy", "IgnorePublicAcls", "RestrictPublicBuckets"]):
                        status = "pass"
                        severity = "low"
                    else:
                        status = "fail"
                        severity = "high"
                except self.s3.exceptions.NoSuchPublicAccessBlockConfiguration:
                    status = "fail"
                    severity = "high"
                
                findings.append({
                    "control_id": "4.1",
                    "title": "Ensure S3 buckets are not publicly accessible",
                    "severity": severity,
                    "status": status,
                    "asset": f"s3://{bucket_name}",
                    "finding": f"Public access: {status == 'fail'}"
                })
            
            return findings
        except Exception as e:
            return [{"control_id": "4.1", "title": str(e), "severity": "medium", "status": "error"}]
    
    def check_s3_encryption(self) -> List[Dict]:
        """CIS 4.2 - Ensure S3 bucket policy is configured to deny unencrypted bucket uploads"""
        try:
            buckets = self.s3.list_buckets()
            findings = []
            
            for bucket in buckets.get("Buckets", []):
                bucket_name = bucket["Name"]
                
                # Check encryption
                try:
                    enc = self.s3.get_bucket_encryption(Bucket=bucket_name)
                    has_encryption = len(enc.get("ServerSideEncryptionConfiguration", [])) > 0
                except self.s3.exceptions.NoSuchBucketEncryption:
                    has_encryption = False
                
                findings.append({
                    "control_id": "4.2",
                    "title": "Ensure S3 bucket policy is configured to deny unencrypted bucket uploads",
                    "severity": "high" if not has_encryption else "low",
                    "status": "fail" if not has_encryption else "pass",
                    "asset": f"s3://{bucket_name}",
                    "finding": f"Encryption enabled: {has_encryption}"
                })
            
            return findings
        except Exception as e:
            return [{"control_id": "4.2", "title": str(e), "severity": "medium", "status": "error"}]
    
    # === KMS Checks ===
    
    def check_kms_key_rotation(self) -> List[Dict]:
        """CIS 4.6 - Ensure KMS key rotation is enabled"""
        try:
            keys = self.kms.list_keys()
            findings = []
            
            for key in keys.get("Keys", []):
                key_id = key["KeyId"]
                
                # Check rotation
                try:
                    rot = self.kms.get_key_rotation_status(KeyId=key_id)
                    enabled = rot.get("KeyRotationEnabled", False)
                except:
                    enabled = False
                
                findings.append({
                    "control_id": "4.6",
                    "title": "Ensure KMS key rotation is enabled",
                    "severity": "medium" if not enabled else "low",
                    "status": "fail" if not enabled else "pass",
                    "asset": f"kms:{key_id}",
                    "finding": f"Rotation enabled: {enabled}"
                })
            
            return findings
        except Exception as e:
            return [{"control_id": "4.6", "title": str(e), "severity": "medium", "status": "error"}]


async def run_boto3_checks(credentials: Dict) -> List[Dict]:
    """Run all boto3 checks"""
    checker = Boto3Checker(credentials)
    return await checker.check_all()


# Example
if __name__ == "__main__":
    async def main():
        creds = {
            "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
            "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        }
        
        findings = await run_boto3_checks(creds)
        
        for f in findings:
            print(f"[{f['status']}] {f['control_id']}: {f['title']}")
    
    asyncio.run(main())