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
# MODELS - COMPANY PARTNERSHIPS (Ethical Exposure Model)
# ============================================================================

class CompanySponsor(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    website: str
    logo_url: str
    
    # Contact
    contact_name: Optional[str] = None
    contact_email: str
    contact_phone: Optional[str] = None
    
    # Agreement
    agreement_status: str = "pending"  # pending, active, inactive
    agreement_date: Optional[datetime] = None
    
    # Terms
    ships_to_members: bool = True
    provides_warranty: bool = True
    fulfillment_terms: Optional[str] = None
    
    # Display
    display_on_homepage: bool = False
    display_order: int = 0
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanySponsorCreate(BaseModel):
    company_name: str
    website: str
    logo_url: str
    contact_email: str
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    fulfillment_terms: Optional[str] = None

class DonatedProduct(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sponsor_id: str
    
    product_name: str
    description: str
    category: str = "general"
    estimated_value: Optional[float] = None
    
    quantity_available: int = 0
    quantity_fulfilled: int = 0
    
    fulfillment_type: str = "direct_ship"  # direct_ship, warehouse, digital
    requires_approval: bool = True
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DonatedProductCreate(BaseModel):
    sponsor_id: str
    product_name: str
    description: str
    category: str = "general"
    estimated_value: Optional[float] = None
    quantity_available: int = 1
    fulfillment_type: str = "direct_ship"

class OutreachCampaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    company_email: str
    company_website: Optional[str] = None
    
    status: str = "pending"  # pending, sent, opened, responded, partnered, declined
    
    email_subject: str
    email_body: str
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class OutreachCampaignCreate(BaseModel):
    company_name: str
    company_email: str
    company_website: Optional[str] = None
    notes: Optional[str] = None

# ============================================================================
# MODELS - CONTRIBUTION OFFERS (Supply Side)
# ============================================================================

class ContributionOffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    contributor_id: Optional[str] = "anonymous"
    
    offer_type: str  # skill, item, knowledge, time, connection, other
    description: str
    category: str = "general"
    
    availability: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    
    # Matching
    matched_request_id: Optional[str] = None
    is_fulfilled: bool = False
    
    # Source tracking
    source: str = "internal_app"  # or "external_poll"
    contact_info: Optional[str] = None  # For external poll follow-ups
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContributionOfferCreate(BaseModel):
    contributor_id: Optional[str] = "anonymous"
    offer_type: str
    description: str
    category: str = "general"
    availability: Optional[str] = None
    location: Optional[str] = None
    tags: List[str] = []
    source: str = "internal_app"
    contact_info: Optional[str] = None

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
# API ROUTES - COMPANY PARTNERSHIPS & OUTREACH
# ============================================================================

@api_router.post("/sponsor", response_model=CompanySponsor)
async def create_sponsor(sponsor_data: CompanySponsorCreate):
    """Add a company sponsor (admin only in production)"""
    sponsor = CompanySponsor(**sponsor_data.model_dump())
    doc = sponsor.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    if doc.get('agreement_date'):
        doc['agreement_date'] = doc['agreement_date'].isoformat()
    
    await db.sponsors.insert_one(doc)
    return sponsor

@api_router.get("/sponsors", response_model=List[CompanySponsor])
async def get_sponsors(active_only: bool = True, for_display: bool = False):
    """Get company sponsors"""
    filter_query = {}
    if active_only:
        filter_query["agreement_status"] = "active"
    if for_display:
        filter_query["display_on_homepage"] = True
    
    sponsors = await db.sponsors.find(filter_query, {"_id": 0}).sort("display_order", 1).to_list(100)
    
    for sponsor in sponsors:
        sponsor['created_at'] = datetime.fromisoformat(sponsor['created_at'])
        sponsor['updated_at'] = datetime.fromisoformat(sponsor['updated_at'])
        if sponsor.get('agreement_date') and isinstance(sponsor['agreement_date'], str):
            sponsor['agreement_date'] = datetime.fromisoformat(sponsor['agreement_date'])
    
    return sponsors

@api_router.patch("/sponsor/{sponsor_id}/activate")
async def activate_sponsor(sponsor_id: str):
    """Activate a sponsor (after agreement signed)"""
    result = await db.sponsors.update_one(
        {"id": sponsor_id},
        {"$set": {
            "agreement_status": "active",
            "agreement_date": datetime.now(timezone.utc).isoformat(),
            "display_on_homepage": True,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    
    return {"message": "Sponsor activated"}

@api_router.post("/donated-product", response_model=DonatedProduct)
async def add_donated_product(product_data: DonatedProductCreate):
    """Add a product donated by a sponsor"""
    product = DonatedProduct(**product_data.model_dump())
    doc = product.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.donated_products.insert_one(doc)
    return product

@api_router.get("/donated-products", response_model=List[DonatedProduct])
async def get_donated_products(
    sponsor_id: Optional[str] = None,
    category: Optional[str] = None,
    available_only: bool = True
):
    """Get donated products catalog"""
    filter_query = {}
    if sponsor_id:
        filter_query["sponsor_id"] = sponsor_id
    if category:
        filter_query["category"] = category
    if available_only:
        filter_query["$expr"] = {"$gt": [{"$subtract": ["$quantity_available", "$quantity_fulfilled"]}, 0]}
    
    products = await db.donated_products.find(filter_query, {"_id": 0}).to_list(100)
    
    for product in products:
        product['created_at'] = datetime.fromisoformat(product['created_at'])
    
    return products

@api_router.post("/outreach", response_model=OutreachCampaign)
async def create_outreach(outreach_data: OutreachCampaignCreate):
    """Create outreach campaign to a company"""
    # Generate email content
    email_subject = f"Invitation to join the greatest social experiment in history"
    
    email_body = f"""Dear {outreach_data.company_name} Team,

We're reaching out to invite you to be part of something extraordinary.

AU4A (Ask Us 4 Anything) is the greatest social experiment in history. We're building a platform where human goodwill becomes reality—where people's wishes are fulfilled not through commerce, but through contribution.

Here's what we're offering:

**What {outreach_data.company_name} Would Provide:**
• Products donated to AU4A members who genuinely need them
• Logo and rights to display on our platform
• Direct shipping to members
• Full warranty on donated products

**What {outreach_data.company_name} Would Receive:**
• Logo display on AU4A homepage (seen by thousands)
• Association with a revolutionary social movement
• Brand exposure tied to generosity, not advertising
• Recognition as a company that gives, not just sells
• Part of internet history

**Important:** This is NOT traditional advertising. There are no product listings on our site. Only your logo, displayed proudly at the bottom of our homepage, representing companies that believe in contribution over extraction.

We don't rank by money. We don't sell placement. We don't do sponsored content.

We only recognize companies willing to genuinely give.

If {outreach_data.company_name} is interested in being part of this movement, we'd love to discuss the partnership details.

Are you ready to be part of something that changes how the internet works?

Best regards,
The AU4A Team

P.S. This isn't a sales pitch. It's an invitation to make history.
"""
    
    campaign = OutreachCampaign(
        **outreach_data.model_dump(),
        email_subject=email_subject,
        email_body=email_body
    )
    
    doc = campaign.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc.get('sent_at'):
        doc['sent_at'] = doc['sent_at'].isoformat()
    if doc.get('opened_at'):
        doc['opened_at'] = doc['opened_at'].isoformat()
    if doc.get('responded_at'):
        doc['responded_at'] = doc['responded_at'].isoformat()
    
    await db.outreach_campaigns.insert_one(doc)
    
    return campaign

@api_router.get("/outreach", response_model=List[OutreachCampaign])
async def get_outreach_campaigns(status: Optional[str] = None, limit: int = 100):
    """Get outreach campaigns"""
    filter_query = {}
    if status:
        filter_query["status"] = status
    
    campaigns = await db.outreach_campaigns.find(filter_query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    for campaign in campaigns:
        campaign['created_at'] = datetime.fromisoformat(campaign['created_at'])
        if campaign.get('sent_at') and isinstance(campaign['sent_at'], str):
            campaign['sent_at'] = datetime.fromisoformat(campaign['sent_at'])
        if campaign.get('opened_at') and isinstance(campaign['opened_at'], str):
            campaign['opened_at'] = datetime.fromisoformat(campaign['opened_at'])
        if campaign.get('responded_at') and isinstance(campaign['responded_at'], str):
            campaign['responded_at'] = datetime.fromisoformat(campaign['responded_at'])
    
    return campaigns

@api_router.patch("/outreach/{campaign_id}/mark-sent")
async def mark_outreach_sent(campaign_id: str):
    """Mark outreach as sent"""
    result = await db.outreach_campaigns.update_one(
        {"id": campaign_id},
        {"$set": {
            "status": "sent",
            "sent_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {"message": "Outreach marked as sent"}

@api_router.get("/match-products/{request_id}")
async def match_donated_products(request_id: str):
    """Find donated products that match a request"""
    request = await db.requests.find_one({"id": request_id}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Simple keyword matching
    request_keywords = request['content'].lower().split()
    
    # Find products with available quantity
    products = await db.donated_products.find(
        {
            "$expr": {"$gt": [{"$subtract": ["$quantity_available", "$quantity_fulfilled"]}, 0]},
            "$or": [
                {"product_name": {"$regex": "|".join(request_keywords[:5]), "$options": "i"}},
                {"description": {"$regex": "|".join(request_keywords[:5]), "$options": "i"}},
                {"category": request['category']}
            ]
        },
        {"_id": 0}
    ).limit(10).to_list(10)
    
    for product in products:
        product['created_at'] = datetime.fromisoformat(product['created_at'])
        # Get sponsor info
        sponsor = await db.sponsors.find_one({"id": product['sponsor_id']}, {"_id": 0})
        if sponsor:
            product['sponsor_name'] = sponsor['company_name']
            product['sponsor_logo'] = sponsor['logo_url']
    
    return {
        "request_id": request_id,
        "request_content": request['content'],
        "matched_products": products
    }

# ============================================================================
# API ROUTES - CONTRIBUTION OFFERS (Supply Side / Ramp-up)
# ============================================================================

@api_router.post("/offer", response_model=ContributionOffer)
async def create_offer(offer_data: ContributionOfferCreate):
    """Submit what you can give/contribute (Supply side)"""
    offer = ContributionOffer(**offer_data.model_dump())
    doc = offer.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.contribution_offers.insert_one(doc)
    return offer

@api_router.get("/offers", response_model=List[ContributionOffer])
async def get_offers(
    offer_type: Optional[str] = None,
    category: Optional[str] = None,
    unfulfilled_only: bool = True,
    limit: int = Query(default=50, le=100)
):
    """Browse contribution offers (what people can give)"""
    filter_query = {}
    if offer_type:
        filter_query["offer_type"] = offer_type
    if category:
        filter_query["category"] = category
    if unfulfilled_only:
        filter_query["is_fulfilled"] = False
    
    offers = await db.contribution_offers.find(filter_query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    
    for offer in offers:
        offer['created_at'] = datetime.fromisoformat(offer['created_at'])
    
    return offers

@api_router.get("/match-offers/{request_id}")
async def match_offers_to_request(request_id: str, limit: int = 10):
    """Find contribution offers that might fulfill a request"""
    # Get the request
    request = await db.requests.find_one({"id": request_id}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Simple keyword matching (can be enhanced with AI)
    request_keywords = request['content'].lower().split()
    
    # Find offers with matching keywords
    offers = await db.contribution_offers.find(
        {
            "is_fulfilled": False,
            "$or": [
                {"description": {"$regex": "|".join(request_keywords[:5]), "$options": "i"}},
                {"category": request['category']},
                {"tags": {"$in": request_keywords[:10]}}
            ]
        },
        {"_id": 0}
    ).limit(limit).to_list(limit)
    
    for offer in offers:
        offer['created_at'] = datetime.fromisoformat(offer['created_at'])
    
    return {
        "request_id": request_id,
        "request_content": request['content'],
        "potential_matches": offers
    }

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
# BLACK BOX - MASTER CONTROL (Hidden from public)
# ============================================================================

from blackbox import blackbox_router, verify_blackbox_access

# Include Black Box router (hidden from OpenAPI docs)
app.include_router(blackbox_router)

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
