# AU4A Contribution Ramp-Up System

## External Giving Poll (Anonymous, No Branding)

### Purpose
Collect contribution offers from social media and free platforms WITHOUT revealing AU4A.

### External Poll URL
```
https://your-domain.com/poll
```

This page:
- ✅ NO AU4A branding
- ✅ NO links back to main site
- ✅ Anonymous contribution collection
- ✅ Minimal, mysterious design
- ✅ Can be shared on Reddit, Twitter, Discord, forums

### Sharing Strategy

**Where to Share:**
- Reddit: r/randomactsofkindness, r/assistance, r/favors
- Twitter: With hashtags like #payitforward #randomactsofkindness
- Discord: Community servers
- Facebook groups: Local giving groups
- Forums: Community boards

**Example Post:**
```
"Simple question: What could you give to someone who needs it?

No strings attached. Just curious what people are willing to share.

[link to /poll]"
```

**DO NOT:**
- Mention AU4A
- Link to main site
- Explain the full system
- Make it commercial

**DO:**
- Keep it mysterious
- Make it about generosity
- Let curiosity drive participation
- Build supply before revealing demand

---

## Internal Contribution Flow

### URL
```
/give
```

### Trigger Points

1. **After First Ask**
   - User submits a request
   - Prompt: "You've asked for something. Would you like to tell us what YOU can give in return?"
   - Redirect to /give

2. **Journey Milestone**
   - Show after certain participation levels
   - Part of unlocking Contribute quadrant

3. **Direct Link**
   - From navigation
   - From profile/journey page

### User Experience

**Step 1:** Introduction
- "You've asked... Now, what can YOU give?"
- Conversational, friendly tone

**Step 2:** Choose Offering Type
- Skill
- Item
- Knowledge
- Time
- Connection

**Step 3:** Describe Offering
- What specifically?
- When/how available?

**Step 4:** Review & Submit
- Can add multiple offerings
- Submit all at once

### Backend Storage

All contributions stored in `contribution_offers` collection:
```json
{
  "id": "uuid",
  "contributor_id": "user_id or anonymous",
  "offer_type": "skill|item|knowledge|time|connection",
  "description": "What they can give",
  "category": "general",
  "availability": "when/how",
  "location": "where (optional)",
  "tags": ["auto-generated", "keywords"],
  "source": "external_poll | internal_app",
  "contact_info": "email (for external poll)",
  "matched_request_id": null,
  "is_fulfilled": false,
  "created_at": "timestamp"
}
```

---

## Matching System

### API Endpoint
```
GET /api/match-offers/{request_id}
```

### How It Works
1. User submits a request (Ask)
2. System searches contribution_offers for matches
3. Keyword matching on description, category, tags
4. Returns potential matches
5. Coordinators can connect request with offer
6. Mark offer as matched/fulfilled

### Example Match Flow

**Request:** "I need help learning Python programming"

**System Finds:**
- Offer 1: "I can teach Python to beginners" (90% match)
- Offer 2: "I have Python books to give away" (70% match)
- Offer 3: "I know online Python resources" (60% match)

**Coordinator:** Reviews matches, contacts contributors, facilitates connection

**Result:** Request fulfilled, offer marked as used

---

## Supply-Side Strategy

### Why This Matters

**Problem:** Wishes without substance = empty promises

**Solution:** Build supply BEFORE demand scales

**Approach:**
1. **External Ramp-up:** Collect anonymous offers via social media (build pool)
2. **Internal Engagement:** Ask users what they can give (reciprocity)
3. **Matching Engine:** Connect supply with demand (coordination)
4. **Fulfillment:** Execute the giving (make wishes real)

### Metrics to Track

- Total contribution offers
- Offers by type (skill/item/knowledge/time/connection)
- Source (external_poll vs internal_app)
- Match rate (offers matched to requests)
- Fulfillment rate (matches that completed)

### Scaling the Supply

1. **Week 1-2:** Launch external poll, share on 5-10 platforms
2. **Week 3-4:** Internal app launches, ask early users to contribute
3. **Month 2:** Have 100+ contribution offers in database
4. **Month 3:** Matching system starts showing results
5. **Month 6:** Self-sustaining supply-demand ecosystem

---

## Important Notes

**External Poll:**
- Keep it anonymous and mysterious
- NO AU4A branding (whisper campaign)
- Collect email for follow-up only
- Build curiosity, not conversions

**Internal Flow:**
- Make giving feel good, not obligatory
- Conversational, friendly tone
- Show impact ("Your contribution could help someone")
- Part of the journey, not a transaction

**Philosophy:**
- Give to get (but not transactional)
- Contribution unlocks features
- Community-driven, not platform-driven
- Goodwill as currency

---

This system builds the **substance** needed for AU4A to fulfill wishes at scale.
