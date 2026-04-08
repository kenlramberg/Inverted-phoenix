"""
THE BLACK BOX - Master Control System
CONFIDENTIAL - Hidden from public

This is the control center for AU4A.
Only accessible by master admin and appointed controllers.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
import os
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection for Black Box
mongo_url = os.environ['MONGO_URL']
bb_client = AsyncIOMotorClient(mongo_url)
db = bb_client[os.environ['DB_NAME']]

# Hidden router - not included in public API docs
# Uses /api/blackbox prefix to ensure proper routing through Kubernetes ingress
blackbox_router = APIRouter(prefix="/api/blackbox", include_in_schema=False)

# Master secret key (set in environment, NEVER commit to git)
MASTER_KEY = os.environ.get('BLACKBOX_MASTER_KEY', secrets.token_urlsafe(32))
CONTROLLERS = {}  # In-memory for now, move to DB in production

# ============================================================================
# AUTHENTICATION
# ============================================================================

def verify_blackbox_access(x_blackbox_key: str = Header(None)):
    """Verify Black Box access key"""
    if not x_blackbox_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Check if master key
    if x_blackbox_key == MASTER_KEY:
        return {"role": "master", "user_id": "master_admin"}
    
    # Check if controller key
    if x_blackbox_key in CONTROLLERS:
        return CONTROLLERS[x_blackbox_key]
    
    raise HTTPException(status_code=403, detail="Invalid Black Box key")

# ============================================================================
# MODELS
# ============================================================================

class Controller(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    access_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    permissions: List[str] = ["code_review", "ethics_review"]  # master has "all"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "master_admin"
    is_active: bool = True

class ControllerCreate(BaseModel):
    name: str
    email: str
    permissions: List[str] = ["code_review", "ethics_review"]

class CodeSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contributor_github: str
    pr_number: Optional[int] = None
    files_changed: List[str] = []
    code_diff: str
    
    # Analysis results
    security_score: Optional[float] = None  # 0-100
    security_issues: List[str] = []
    ai_review_summary: Optional[str] = None
    
    # Review status
    status: str = "pending"  # pending, approved, rejected, changes_requested
    reviewed_by: Optional[str] = None
    review_comments: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CodeSubmissionReview(BaseModel):
    status: Literal["approved", "rejected", "changes_requested"]
    comments: str

class EthicsCase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    request_content: str
    
    # Automated scores (from AI + community)
    ai_legality_score: float
    ai_morality_score: float
    ai_harm_score: float
    community_evaluation_count: int
    community_scores_avg: dict
    
    # Why it needs human review
    reason: str  # "ambiguous_ai_score", "community_split", "edge_case"
    
    # Human decision
    decision: Optional[str] = None  # "approve", "reject", "request_more_info"
    decided_by: Optional[str] = None
    decision_rationale: Optional[str] = None
    decided_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EthicsDecision(BaseModel):
    decision: Literal["approve", "reject", "request_more_info"]
    rationale: str

class TaskArbitration(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    issue_type: str  # "no_matches", "multiple_conflicts", "stuck", "error"
    description: str
    
    # Proposed solutions
    suggested_actions: List[str] = []
    
    # Human decision
    action_taken: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SystemOverride(BaseModel):
    action: str
    reason: str
    target_id: Optional[str] = None

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str
    performed_by: str
    target_type: str  # "code_submission", "ethics_case", "task", "controller", "system"
    target_id: str
    details: dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ============================================================================
# CONTROLLER MANAGEMENT
# ============================================================================

@blackbox_router.post("/controllers", response_model=Controller)
async def create_controller(
    controller_data: ControllerCreate,
    auth: dict = Depends(verify_blackbox_access)
):
    """Create a new controller (master only)"""
    if auth["role"] != "master":
        raise HTTPException(status_code=403, detail="Only master admin can create controllers")
    
    controller = Controller(**controller_data.model_dump())
    
    # Store in database
    doc = controller.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.blackbox_controllers.insert_one(doc)
    
    # Add to in-memory cache
    CONTROLLERS[controller.access_key] = {
        "role": "controller",
        "user_id": controller.id,
        "permissions": controller.permissions
    }
    
    # Audit log
    await log_audit_action("create_controller", auth["user_id"], "controller", controller.id, {"name": controller.name})
    
    return controller

@blackbox_router.get("/controllers", response_model=List[Controller])
async def list_controllers(auth: dict = Depends(verify_blackbox_access)):
    """List all controllers (master only)"""
    if auth["role"] != "master":
        raise HTTPException(status_code=403, detail="Only master admin can list controllers")
    
    controllers = await db.blackbox_controllers.find({"is_active": True}, {"_id": 0}).to_list(100)
    for c in controllers:
        c['created_at'] = datetime.fromisoformat(c['created_at'])
    return controllers

@blackbox_router.delete("/controllers/{controller_id}")
async def revoke_controller(controller_id: str, auth: dict = Depends(verify_blackbox_access)):
    """Revoke controller access (master only)"""
    if auth["role"] != "master":
        raise HTTPException(status_code=403, detail="Only master admin can revoke controllers")
    
    result = await db.blackbox_controllers.update_one(
        {"id": controller_id},
        {"$set": {"is_active": False}}
    )
    
    # Remove from memory cache
    controller = await db.blackbox_controllers.find_one({"id": controller_id})
    if controller and controller['access_key'] in CONTROLLERS:
        del CONTROLLERS[controller['access_key']]
    
    await log_audit_action("revoke_controller", auth["user_id"], "controller", controller_id, {})
    
    return {"message": "Controller access revoked"}

# ============================================================================
# CODE REVIEW QUEUE
# ============================================================================

@blackbox_router.post("/code-submissions", response_model=CodeSubmission)
async def submit_code_for_review(
    submission: dict,
    auth: dict = Depends(verify_blackbox_access)
):
    """Submit code for Black Box review (automated or manual submission)"""
    # This would typically be called by CI/CD when programmer submits PR
    
    code_submission = CodeSubmission(**submission)
    
    # Run automated security analysis
    security_result = await analyze_code_security(code_submission.code_diff, code_submission.files_changed)
    code_submission.security_score = security_result["score"]
    code_submission.security_issues = security_result["issues"]
    
    # Run AI code review
    ai_review = await ai_code_review(code_submission.code_diff)
    code_submission.ai_review_summary = ai_review
    
    # Store in database
    doc = code_submission.model_dump()
    doc['submitted_at'] = doc['submitted_at'].isoformat()
    if doc.get('reviewed_at'):
        doc['reviewed_at'] = doc['reviewed_at'].isoformat()
    
    await db.blackbox_code_submissions.insert_one(doc)
    
    await log_audit_action("code_submitted", submission.get("contributor_github", "unknown"), "code_submission", code_submission.id, {"files": len(code_submission.files_changed)})
    
    return code_submission

@blackbox_router.get("/code-submissions", response_model=List[CodeSubmission])
async def list_code_submissions(
    status: Optional[str] = "pending",
    auth: dict = Depends(verify_blackbox_access)
):
    """List code submissions awaiting review"""
    if "code_review" not in auth.get("permissions", []) and auth["role"] != "master":
        raise HTTPException(status_code=403, detail="No code review permission")
    
    filter_query = {}
    if status:
        filter_query["status"] = status
    
    submissions = await db.blackbox_code_submissions.find(filter_query, {"_id": 0}).sort("submitted_at", 1).to_list(100)
    
    for sub in submissions:
        sub['submitted_at'] = datetime.fromisoformat(sub['submitted_at'])
        if sub.get('reviewed_at'):
            sub['reviewed_at'] = datetime.fromisoformat(sub['reviewed_at'])
    
    return submissions

@blackbox_router.patch("/code-submissions/{submission_id}")
async def review_code_submission(
    submission_id: str,
    review: CodeSubmissionReview,
    auth: dict = Depends(verify_blackbox_access)
):
    """Review and approve/reject code submission"""
    if "code_review" not in auth.get("permissions", []) and auth["role"] != "master":
        raise HTTPException(status_code=403, detail="No code review permission")
    
    result = await db.blackbox_code_submissions.update_one(
        {"id": submission_id},
        {"$set": {
            "status": review.status,
            "review_comments": review.comments,
            "reviewed_by": auth["user_id"],
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    await log_audit_action("code_reviewed", auth["user_id"], "code_submission", submission_id, {"decision": review.status})
    
    return {"message": f"Code submission {review.status}"}

# ============================================================================
# CODE ANALYSIS ENGINE
# ============================================================================

async def analyze_code_security(code_diff: str, files_changed: List[str]) -> dict:
    """Analyze code for security issues"""
    issues = []
    score = 100.0
    
    # Pattern matching for suspicious code
    suspicious_patterns = [
        ("eval(", "Use of eval() - potential code injection"),
        ("exec(", "Use of exec() - potential code injection"),
        ("__import__", "Dynamic imports - potential backdoor"),
        ("os.system", "Direct system calls - security risk"),
        ("subprocess.call", "Subprocess execution - validate carefully"),
        ("pickle.loads", "Pickle deserialization - unsafe"),
        ("yaml.load", "YAML load without safe_load - unsafe"),
        ("rm -rf", "Dangerous file deletion command"),
        ("DROP TABLE", "SQL DROP statement - verify intent"),
        ("DELETE FROM", "SQL DELETE - verify intent"),
        ("base64.b64decode", "Base64 decode - check for obfuscation"),
        ("requests.get", "External HTTP request - verify URL"),
        ("open(", "File operations - verify paths"),
    ]
    
    for pattern, warning in suspicious_patterns:
        if pattern in code_diff:
            issues.append(warning)
            score -= 10
    
    # Check for hardcoded secrets
    secret_patterns = [
        "password =",
        "api_key =",
        "secret =",
        "token =",
        "private_key =",
    ]
    
    for pattern in secret_patterns:
        if pattern in code_diff and "=" in code_diff:
            issues.append(f"Potential hardcoded secret: {pattern}")
            score -= 15
    
    # Check for obfuscation
    if len([line for line in code_diff.split('\n') if len(line) > 200]) > 3:
        issues.append("Unusually long lines - potential obfuscation")
        score -= 20
    
    score = max(0, score)
    
    return {
        "score": score,
        "issues": issues
    }

async def ai_code_review(code_diff: str) -> str:
    """AI-powered code review using GPT-5.2"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=os.environ.get('EMERGENT_LLM_KEY'),
            session_id=f"code_review_{uuid.uuid4()}",
            system_message="""You are a security-focused code reviewer for AU4A.

Your job:
1. Identify security vulnerabilities
2. Detect malicious code patterns
3. Check for backdoors or hidden functionality
4. Verify code quality and best practices
5. Flag anything suspicious

Be thorough and critical. This code will run on a live platform serving real users."""
        ).with_model("openai", "gpt-5.2")
        
        prompt = f"""Review this code diff for security issues and quality:

```diff
{code_diff[:5000]}  # Limit to 5000 chars
```

Provide:
1. Security concerns (if any)
2. Code quality issues
3. Recommendation (approve/reject/changes needed)
4. Overall assessment"""
        
        response = await chat.send_message(UserMessage(text=prompt))
        return response.strip()
        
    except Exception as e:
        return f"AI review failed: {str(e)}"

# ============================================================================
# ETHICS ARBITRATION
# ============================================================================

@blackbox_router.get("/ethics-cases", response_model=List[EthicsCase])
async def list_ethics_cases(
    pending_only: bool = True,
    auth: dict = Depends(verify_blackbox_access)
):
    """List ethics cases needing human review"""
    if "ethics_review" not in auth.get("permissions", []) and auth["role"] != "master":
        raise HTTPException(status_code=403, detail="No ethics review permission")
    
    filter_query = {}
    if pending_only:
        filter_query["decision"] = None
    
    cases = await db.blackbox_ethics_cases.find(filter_query, {"_id": 0}).sort("created_at", 1).to_list(100)
    
    for case in cases:
        case['created_at'] = datetime.fromisoformat(case['created_at'])
        if case.get('decided_at'):
            case['decided_at'] = datetime.fromisoformat(case['decided_at'])
    
    return cases

@blackbox_router.patch("/ethics-cases/{case_id}")
async def decide_ethics_case(
    case_id: str,
    decision: EthicsDecision,
    auth: dict = Depends(verify_blackbox_access)
):
    """Make final decision on ethics case"""
    if "ethics_review" not in auth.get("permissions", []) and auth["role"] != "master":
        raise HTTPException(status_code=403, detail="No ethics review permission")
    
    result = await db.blackbox_ethics_cases.update_one(
        {"id": case_id},
        {"$set": {
            "decision": decision.decision,
            "decision_rationale": decision.rationale,
            "decided_by": auth["user_id"],
            "decided_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Update the actual request based on decision
    case = await db.blackbox_ethics_cases.find_one({"id": case_id})
    if case:
        new_status = "approved" if decision.decision == "approve" else "rejected"
        await db.requests.update_one(
            {"id": case['request_id']},
            {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    
    await log_audit_action("ethics_decided", auth["user_id"], "ethics_case", case_id, {"decision": decision.decision})
    
    return {"message": f"Ethics case {decision.decision}"}

# ============================================================================
# TASK ARBITRATION
# ============================================================================

@blackbox_router.get("/task-arbitrations", response_model=List[TaskArbitration])
async def list_task_arbitrations(
    pending_only: bool = True,
    auth: dict = Depends(verify_blackbox_access)
):
    """List tasks needing arbitration"""
    filter_query = {}
    if pending_only:
        filter_query["action_taken"] = None
    
    tasks = await db.blackbox_task_arbitrations.find(filter_query, {"_id": 0}).sort("created_at", 1).to_list(100)
    
    for task in tasks:
        task['created_at'] = datetime.fromisoformat(task['created_at'])
        if task.get('resolved_at'):
            task['resolved_at'] = datetime.fromisoformat(task['resolved_at'])
    
    return tasks

@blackbox_router.patch("/task-arbitrations/{task_id}")
async def resolve_task_arbitration(
    task_id: str,
    resolution: dict,
    auth: dict = Depends(verify_blackbox_access)
):
    """Resolve a stuck task"""
    result = await db.blackbox_task_arbitrations.update_one(
        {"id": task_id},
        {"$set": {
            "action_taken": resolution.get("action"),
            "resolution_notes": resolution.get("notes"),
            "resolved_by": auth["user_id"],
            "resolved_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    await log_audit_action("task_resolved", auth["user_id"], "task_arbitration", task_id, resolution)
    
    return {"message": "Task arbitration resolved"}

# ============================================================================
# SYSTEM OVERRIDES & EMERGENCY CONTROLS
# ============================================================================

@blackbox_router.post("/system/override")
async def system_override(
    override: SystemOverride,
    auth: dict = Depends(verify_blackbox_access)
):
    """Master override for system actions"""
    if auth["role"] != "master":
        raise HTTPException(status_code=403, detail="Only master admin can override system")
    
    # Log the override
    await log_audit_action("system_override", auth["user_id"], "system", override.target_id or "global", {
        "action": override.action,
        "reason": override.reason
    })
    
    # Execute override action
    # (Implementation depends on specific override actions)
    
    return {"message": f"System override executed: {override.action}"}

@blackbox_router.post("/system/emergency-disable")
async def emergency_disable(
    reason: str,
    auth: dict = Depends(verify_blackbox_access)
):
    """EMERGENCY: Disable entire platform (master only)"""
    if auth["role"] != "master":
        raise HTTPException(status_code=403, detail="Only master admin can emergency disable")
    
    # Set global disable flag
    await db.system_settings.update_one(
        {"key": "platform_enabled"},
        {"$set": {"value": False, "disabled_reason": reason, "disabled_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    await log_audit_action("emergency_disable", auth["user_id"], "system", "global", {"reason": reason})
    
    return {"message": "PLATFORM DISABLED", "reason": reason}

# ============================================================================
# AUDIT LOGGING
# ============================================================================

async def log_audit_action(action: str, performed_by: str, target_type: str, target_id: str, details: dict):
    """Log all Black Box actions for audit trail"""
    log = AuditLog(
        action=action,
        performed_by=performed_by,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    
    doc = log.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.blackbox_audit_logs.insert_one(doc)

@blackbox_router.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    limit: int = 100,
    auth: dict = Depends(verify_blackbox_access)
):
    """Get audit logs (master only)"""
    if auth["role"] != "master":
        raise HTTPException(status_code=403, detail="Only master admin can view audit logs")
    
    logs = await db.blackbox_audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    
    for log in logs:
        log['timestamp'] = datetime.fromisoformat(log['timestamp'])
    
    return logs

# ============================================================================
# DASHBOARD / METRICS
# ============================================================================

@blackbox_router.get("/dashboard")
async def get_dashboard_metrics(auth: dict = Depends(verify_blackbox_access)):
    """Get Black Box dashboard metrics"""
    
    # Code submissions stats
    pending_code = await db.blackbox_code_submissions.count_documents({"status": "pending"})
    approved_code = await db.blackbox_code_submissions.count_documents({"status": "approved"})
    rejected_code = await db.blackbox_code_submissions.count_documents({"status": "rejected"})
    
    # Ethics cases stats
    pending_ethics = await db.blackbox_ethics_cases.count_documents({"decision": None})
    decided_ethics = await db.blackbox_ethics_cases.count_documents({"decision": {"$ne": None}})
    
    # Task arbitrations
    pending_tasks = await db.blackbox_task_arbitrations.count_documents({"action_taken": None})
    
    # System health
    total_users = await db.users.count_documents({})
    total_requests = await db.requests.count_documents({})
    
    return {
        "code_review": {
            "pending": pending_code,
            "approved": approved_code,
            "rejected": rejected_code
        },
        "ethics": {
            "pending": pending_ethics,
            "decided": decided_ethics
        },
        "tasks": {
            "pending": pending_tasks
        },
        "platform": {
            "total_users": total_users,
            "total_requests": total_requests
        }
    }
