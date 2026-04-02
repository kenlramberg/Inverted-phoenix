from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Literal
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="AU4A - Ask Us 4 Anything")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============================================================================
# ENUMS & TYPES
# ============================================================================

class RequestStatus(str, Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"

class ContributionType(str, Enum):
    BORROW = "borrow"
    BARTER = "barter"
    BUY = "buy"
    BRING = "bring"
    BESTOW = "bestow"
    BEFRIEND = "befriend"

class ContributionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"

class CoordinationStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class ExecutionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"

# ============================================================================
# MODELS - A: ASK LAYER
# ============================================================================

class Request(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    category: str = "general"
    status: RequestStatus = RequestStatus.PENDING
    
    # Ethics scores (averaged from evaluations)
    ethical_score: Optional[float] = None
    harm_score: Optional[float] = None
    legality_score: Optional[float] = None
    cultural_impact_score: Optional[float] = None
    
    # Evaluation tracking
    evaluation_count: int = 0
    required_evaluations: int = 3  # Can scale up as platform grows
    
    # User tracking
    submitted_by: Optional[str] = None  # user_id or "anonymous"
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RequestCreate(BaseModel):
    content: str
    category: str = "general"
    submitted_by: Optional[str] = "anonymous"

# ============================================================================
# MODELS - ETHICS ENGINE
# ============================================================================

class Evaluation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    evaluator_id: str
    
    # Scores (1-10 scale)
    legality_score: int = Field(ge=1, le=10)
    morality_score: int = Field(ge=1, le=10)
    harm_score: int = Field(ge=1, le=10)  # Higher = more harmful
    cultural_impact_score: int = Field(ge=1, le=10)
    
    comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EvaluationCreate(BaseModel):
    request_id: str
    evaluator_id: str
    legality_score: int = Field(ge=1, le=10)
    morality_score: int = Field(ge=1, le=10)
    harm_score: int = Field(ge=1, le=10)
    cultural_impact_score: int = Field(ge=1, le=10)
    comments: Optional[str] = None

# ============================================================================
# MODELS - B: CONTRIBUTE LAYER
# ============================================================================

class Contribution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    contributor_id: str
    
    contribution_type: ContributionType
    content: str
    details: Optional[str] = None
    trade_offer: Optional[str] = None  # For barter
    
    status: ContributionStatus = ContributionStatus.PENDING
    verified: bool = False
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContributionCreate(BaseModel):
    request_id: str
    contributor_id: str
    contribution_type: ContributionType
    content: str
    details: Optional[str] = None
    trade_offer: Optional[str] = None

# ============================================================================
# MODELS - C: COORDINATE LAYER
# ============================================================================

class CoordinationTask(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    coordinator_id: str
    
    strategy: str
    resources_needed: List[str] = []
    collaborators: List[str] = []
    
    status: CoordinationStatus = CoordinationStatus.PLANNING
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CoordinationTaskCreate(BaseModel):
    request_id: str
    coordinator_id: str
    strategy: str
    resources_needed: List[str] = []
    collaborators: List[str] = []

class CoordinationTaskUpdate(BaseModel):
    strategy: Optional[str] = None
    resources_needed: Optional[List[str]] = None
    collaborators: Optional[List[str]] = None
    status: Optional[CoordinationStatus] = None

# ============================================================================
# MODELS - D: EXECUTE LAYER
# ============================================================================

class Execution(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    coordination_id: Optional[str] = None
    executor_id: str
    
    action_taken: str
    verification_proof: Optional[str] = None
    
    status: ExecutionStatus = ExecutionStatus.IN_PROGRESS
    
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ExecutionCreate(BaseModel):
    request_id: str
    coordination_id: Optional[str] = None
    executor_id: str
    action_taken: str
    verification_proof: Optional[str] = None

class ExecutionVerify(BaseModel):
    verification_proof: str

# ============================================================================
# MODELS - SEARCH ENGINE / KNOWLEDGE BASE
# ============================================================================

class KnowledgeEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fulfilled_request_id: str
    
    title: str
    content: str
    keywords: List[str] = []
    category: str = "general"
    
    verified: bool = False
    quality_score: float = 0.0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KnowledgeEntryCreate(BaseModel):
    fulfilled_request_id: str
    title: str
    content: str
    keywords: List[str] = []
    category: str = "general"

# ============================================================================
# MODELS - USER
# ============================================================================

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    anonymous_id: Optional[str] = None
    
    email: Optional[str] = None
    username: Optional[str] = None
    
    # Participation metrics
    reputation_score: float = 0.0
    participation_level: int = 0  # 0-10, unlocks features
    
    total_asks: int = 0
    total_contributions: int = 0
    total_evaluations: int = 0
    total_coordinations: int = 0
    total_executions: int = 0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_active: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    anonymous_id: Optional[str] = None

class UserStats(BaseModel):
    id: str
    reputation_score: float
    participation_level: int
    total_asks: int
    total_contributions: int
    total_evaluations: int
    total_coordinations: int
    total_executions: int

# ============================================================================
# API ROUTES - A: ASK LAYER
# ============================================================================

@api_router.post("/ask", response_model=Request)
async def create_request(req: RequestCreate):
    """Submit a new request (Ask layer)"""
    request_obj = Request(**req.model_dump())
    doc = request_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.requests.insert_one(doc)
    
    # Update user stats if not anonymous
    if req.submitted_by and req.submitted_by != "anonymous":
        await db.users.update_one(
            {"id": req.submitted_by},
            {"$inc": {"total_asks": 1}, "$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
        )
    
    return request_obj

@api_router.get("/requests", response_model=List[Request])
async def get_requests(
    status: Optional[RequestStatus] = None,
    category: Optional[str] = None,
    limit: int = Query(default=50, le=100)
):
    """Browse requests with optional filters"""
    filter_query = {}
    if status:
        filter_query["status"] = status.value
    if category:
        filter_query["category"] = category
    
    requests = await db.requests.find(filter_query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    # Convert ISO strings back to datetime
    for req in requests:
        req['created_at'] = datetime.fromisoformat(req['created_at'])
        req['updated_at'] = datetime.fromisoformat(req['updated_at'])
    
    return requests

@api_router.get("/request/{request_id}", response_model=Request)
async def get_request(request_id: str):
    """Get single request details"""
    req = await db.requests.find_one({"id": request_id}, {"_id": 0})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    req['created_at'] = datetime.fromisoformat(req['created_at'])
    req['updated_at'] = datetime.fromisoformat(req['updated_at'])
    return req

# ============================================================================
# API ROUTES - ETHICS ENGINE
# ============================================================================

@api_router.post("/evaluate", response_model=Evaluation)
async def create_evaluation(eval_data: EvaluationCreate):
    """Submit an ethical evaluation for a request"""
    evaluation = Evaluation(**eval_data.model_dump())
    doc = evaluation.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.evaluations.insert_one(doc)
    
    # Update request evaluation count and scores
    await update_request_scores(eval_data.request_id)
    
    # Update user stats
    await db.users.update_one(
        {"id": eval_data.evaluator_id},
        {"$inc": {"total_evaluations": 1}, "$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
    )
    
    return evaluation

@api_router.get("/evaluate/pending", response_model=List[Request])
async def get_pending_evaluations(limit: int = Query(default=10, le=50)):
    """Get requests that need evaluation"""
    # Find requests that haven't met required evaluations yet
    requests = await db.requests.find(
        {"status": RequestStatus.PENDING.value},
        {"_id": 0}
    ).sort("created_at", 1).limit(limit).to_list(limit)
    
    for req in requests:
        req['created_at'] = datetime.fromisoformat(req['created_at'])
        req['updated_at'] = datetime.fromisoformat(req['updated_at'])
    
    return requests

@api_router.get("/evaluate/{request_id}", response_model=List[Evaluation])
async def get_evaluations(request_id: str):
    """Get all evaluations for a request"""
    evaluations = await db.evaluations.find({"request_id": request_id}, {"_id": 0}).to_list(100)
    
    for eval in evaluations:
        eval['timestamp'] = datetime.fromisoformat(eval['timestamp'])
    
    return evaluations

async def update_request_scores(request_id: str):
    """Recalculate request scores based on all evaluations"""
    evaluations = await db.evaluations.find({"request_id": request_id}).to_list(100)
    
    if not evaluations:
        return
    
    count = len(evaluations)
    avg_legality = sum(e['legality_score'] for e in evaluations) / count
    avg_morality = sum(e['morality_score'] for e in evaluations) / count
    avg_harm = sum(e['harm_score'] for e in evaluations) / count
    avg_cultural = sum(e['cultural_impact_score'] for e in evaluations) / count
    
    # Calculate overall ethical score (higher is better)
    # Legality and morality are positive, harm is negative (inverted)
    ethical_score = (avg_legality + avg_morality + (11 - avg_harm) + avg_cultural) / 4
    
    # Determine status based on scores and evaluation count
    req = await db.requests.find_one({"id": request_id})
    required = req.get('required_evaluations', 3)
    
    new_status = RequestStatus.EVALUATING.value
    if count >= required:
        # Auto-reject if harm is too high or legality/morality too low
        if avg_harm > 7 or avg_legality < 4 or avg_morality < 4:
            new_status = RequestStatus.REJECTED.value
        elif ethical_score >= 7:
            new_status = RequestStatus.APPROVED.value
        else:
            new_status = RequestStatus.EVALUATING.value  # Needs more reviews
    
    await db.requests.update_one(
        {"id": request_id},
        {
            "$set": {
                "evaluation_count": count,
                "ethical_score": ethical_score,
                "harm_score": avg_harm,
                "legality_score": avg_legality,
                "cultural_impact_score": avg_cultural,
                "status": new_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )

# ============================================================================
# API ROUTES - B: CONTRIBUTE LAYER
# ============================================================================

@api_router.post("/contribute", response_model=Contribution)
async def create_contribution(contrib: ContributionCreate):
    """Submit a contribution to fulfill a request"""
    contribution = Contribution(**contrib.model_dump())
    doc = contribution.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.contributions.insert_one(doc)
    
    # Update user stats
    await db.users.update_one(
        {"id": contrib.contributor_id},
        {"$inc": {"total_contributions": 1}, "$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
    )
    
    return contribution

@api_router.get("/contributions/{request_id}", response_model=List[Contribution])
async def get_contributions(request_id: str):
    """Get all contributions for a request"""
    contributions = await db.contributions.find({"request_id": request_id}, {"_id": 0}).to_list(100)
    
    for contrib in contributions:
        contrib['timestamp'] = datetime.fromisoformat(contrib['timestamp'])
    
    return contributions

@api_router.patch("/contribution/{contribution_id}/accept")
async def accept_contribution(contribution_id: str):
    """Accept a contribution"""
    result = await db.contributions.update_one(
        {"id": contribution_id},
        {"$set": {"status": ContributionStatus.ACCEPTED.value}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Contribution not found")
    
    # Update request status to in_progress
    contribution = await db.contributions.find_one({"id": contribution_id})
    await db.requests.update_one(
        {"id": contribution['request_id']},
        {"$set": {"status": RequestStatus.IN_PROGRESS.value, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"message": "Contribution accepted"}

# ============================================================================
# API ROUTES - C: COORDINATE LAYER
# ============================================================================

@api_router.post("/coordinate", response_model=CoordinationTask)
async def create_coordination(coord: CoordinationTaskCreate):
    """Create a coordination task"""
    task = CoordinationTask(**coord.model_dump())
    doc = task.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.coordination_tasks.insert_one(doc)
    
    # Update user stats
    await db.users.update_one(
        {"id": coord.coordinator_id},
        {"$inc": {"total_coordinations": 1}, "$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
    )
    
    return task

@api_router.get("/coordinate/{request_id}", response_model=List[CoordinationTask])
async def get_coordination_tasks(request_id: str):
    """Get coordination tasks for a request"""
    tasks = await db.coordination_tasks.find({"request_id": request_id}, {"_id": 0}).to_list(100)
    
    for task in tasks:
        task['created_at'] = datetime.fromisoformat(task['created_at'])
        task['updated_at'] = datetime.fromisoformat(task['updated_at'])
    
    return tasks

@api_router.patch("/coordinate/{task_id}")
async def update_coordination(task_id: str, update: CoordinationTaskUpdate):
    """Update a coordination task"""
    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    result = await db.coordination_tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Coordination task not found")
    
    return {"message": "Coordination task updated"}

# ============================================================================
# API ROUTES - D: EXECUTE LAYER
# ============================================================================

@api_router.post("/execute", response_model=Execution)
async def create_execution(exec_data: ExecutionCreate):
    """Log an execution action"""
    execution = Execution(**exec_data.model_dump())
    doc = execution.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    await db.executions.insert_one(doc)
    
    # Update user stats
    await db.users.update_one(
        {"id": exec_data.executor_id},
        {"$inc": {"total_executions": 1}, "$set": {"last_active": datetime.now(timezone.utc).isoformat()}}
    )
    
    return execution

@api_router.get("/execute/{request_id}", response_model=List[Execution])
async def get_executions(request_id: str):
    """Get execution history for a request"""
    executions = await db.executions.find({"request_id": request_id}, {"_id": 0}).to_list(100)
    
    for exec in executions:
        exec['timestamp'] = datetime.fromisoformat(exec['timestamp'])
    
    return executions

@api_router.patch("/execute/{execution_id}/verify")
async def verify_execution(execution_id: str, verify_data: ExecutionVerify):
    """Verify execution completion"""
    result = await db.executions.update_one(
        {"id": execution_id},
        {"$set": {
            "status": ExecutionStatus.VERIFIED.value,
            "verification_proof": verify_data.verification_proof
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check if request should be marked as fulfilled
    execution = await db.executions.find_one({"id": execution_id})
    executions = await db.executions.find({"request_id": execution['request_id']}).to_list(100)
    
    # If all executions are verified, mark request as fulfilled
    all_verified = all(e['status'] == ExecutionStatus.VERIFIED.value for e in executions)
    if all_verified and executions:
        await db.requests.update_one(
            {"id": execution['request_id']},
            {"$set": {
                "status": RequestStatus.FULFILLED.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Add to knowledge base
        request = await db.requests.find_one({"id": execution['request_id']})
        if request:
            knowledge_entry = KnowledgeEntry(
                fulfilled_request_id=execution['request_id'],
                title=request['content'][:100],
                content=request['content'],
                category=request['category'],
                verified=True,
                quality_score=request.get('ethical_score', 0)
            )
            doc = knowledge_entry.model_dump()
            doc['created_at'] = doc['created_at'].isoformat()
            await db.knowledge_base.insert_one(doc)
    
    return {"message": "Execution verified"}

# ============================================================================
# API ROUTES - SEARCH ENGINE (HYBRID: AU4A + AI WEB SEARCH)
# ============================================================================

from ai_search import hybrid_search

@api_router.get("/search")
async def search_knowledge(q: str = Query(..., min_length=1), limit: int = Query(default=20, le=100)):
    """
    Hybrid AI search engine:
    1. Search AU4A knowledge base first (human-curated, verified)
    2. If < 3 results, search the web with AI (no ad bias)
    3. Return combined results with clear source labels
    """
    # Step 1: Search internal knowledge base
    internal_results = await db.knowledge_base.find(
        {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"content": {"$regex": q, "$options": "i"}},
                {"keywords": {"$in": [q.lower()]}}
            ],
            "verified": True
        },
        {"_id": 0}
    ).sort("quality_score", -1).limit(limit).to_list(limit)
    
    # Convert datetime
    for entry in internal_results:
        entry['created_at'] = datetime.fromisoformat(entry['created_at']) if isinstance(entry.get('created_at'), str) else entry.get('created_at')
    
    # Step 2: If insufficient internal results, use hybrid AI search
    if len(internal_results) < 3:
        hybrid_results = await hybrid_search(q, internal_results, max_total=limit)
        return hybrid_results
    else:
        # Enough internal results - return only AU4A knowledge
        return {
            'query': q,
            'internal_count': len(internal_results),
            'external_count': 0,
            'results': [{**r, 'result_source': 'au4a', 'verified': True} for r in internal_results]
        }


# ============================================================================
# API ROUTES - USER
# ============================================================================

@api_router.post("/user", response_model=User)
async def create_user(user_data: UserCreate):
    """Create a new user (or anonymous user)"""
    user = User(**user_data.model_dump())
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['last_active'] = doc['last_active'].isoformat()
    
    await db.users.insert_one(doc)
    return user

@api_router.get("/user/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: str):
    """Get user statistics"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserStats(**user)

@api_router.get("/user/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user's participation level and unlocked features"""
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate participation level (0-10) based on activity
    total_actions = (
        user['total_asks'] +
        user['total_contributions'] +
        user['total_evaluations'] +
        user['total_coordinations'] +
        user['total_executions']
    )
    
    # Progressive levels: 0, 5, 15, 30, 50, 75, 100, 150, 200, 300, 500+
    level_thresholds = [0, 5, 15, 30, 50, 75, 100, 150, 200, 300, 500]
    participation_level = 0
    for i, threshold in enumerate(level_thresholds):
        if total_actions >= threshold:
            participation_level = i
    
    # Update participation level
    if participation_level != user['participation_level']:
        await db.users.update_one(
            {"id": user_id},
            {"$set": {"participation_level": participation_level}}
        )
    
    # Define unlocked features based on level
    unlocked_features = []
    if participation_level >= 0:
        unlocked_features.append("ask")
    if participation_level >= 1:
        unlocked_features.append("evaluate")
    if participation_level >= 2:
        unlocked_features.append("contribute")
    if participation_level >= 4:
        unlocked_features.append("coordinate")
    if participation_level >= 6:
        unlocked_features.append("execute")
    if participation_level >= 8:
        unlocked_features.append("advanced_search")
    if participation_level >= 10:
        unlocked_features.append("all")
    
    return {
        "user_id": user_id,
        "participation_level": participation_level,
        "total_actions": total_actions,
        "unlocked_features": unlocked_features,
        "next_level_threshold": level_thresholds[min(participation_level + 1, len(level_thresholds) - 1)]
    }

# ============================================================================
# ROOT & HEALTH CHECK
# ============================================================================

@api_router.get("/")
async def root():
    return {
        "message": "AU4A API - Ask Us 4 Anything",
        "tagline": "Do you want the answers 2 everything...?",
        "status": "operational"
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
