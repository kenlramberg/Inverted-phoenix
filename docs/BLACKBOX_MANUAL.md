# THE BLACK BOX - Master Control System

## ⚠️ CONFIDENTIAL - FOR MASTER ADMIN ONLY

**DO NOT share this document publicly. DO NOT commit to public GitHub.**

---

## What is The Black Box?

The Black Box is the **hidden control center** of AU4A. It's the master override system that ensures:
- Code contributions are secure
- Ethical decisions are sound
- System integrity is maintained
- Platform can't be hijacked or corrupted

**Only you (master admin) and appointed controllers have access.**

---

## Access

### URL
```
https://askus4anything.com/blackbox
```

**This URL is NOT linked anywhere on the public site. Memorize it.**

### Authentication

**Master Key:**
- Stored in `/app/backend/.env` as `BLACKBOX_MASTER_KEY`
- Generated on first setup (64-character random string)
- NEVER commit to git
- NEVER share with anyone
- Rotate periodically (monthly recommended)

**To Get Your Master Key:**
```bash
cat /app/backend/.env | grep BLACKBOX_MASTER_KEY
```

Copy the key and save it securely (password manager recommended).

**Login:**
1. Navigate to `/blackbox`
2. Enter your master key
3. Click "Authenticate"
4. You're in.

---

## Features

### 1. CODE REVIEW QUEUE

**Purpose:** Approve all programmer contributions before they merge.

**Flow:**
1. Programmer submits pull request on GitHub
2. CI/CD automatically sends code to Black Box
3. Automated security scan runs
4. AI code review (GPT-5.2) analyzes code
5. Code appears in your review queue
6. You review and decide: Approve / Request Changes / Reject

**Security Analysis:**
- Pattern matching for malicious code (eval, exec, system calls)
- Hardcoded secrets detection (API keys, passwords)
- Obfuscation detection (unusually long lines)
- Dependency vulnerability scanning
- AI-powered backdoor detection

**What You See:**
- Contributor name
- Files changed
- Security score (0-100)
- List of security issues
- AI review summary
- Code diff

**Actions:**
- **Approve** → Code gets merged, contributor gets credit
- **Request Changes** → Programmer must fix issues
- **Reject** → Code is blocked, logged for audit

---

### 2. ETHICS ARBITRATION

**Purpose:** Make final decisions on ambiguous ethical cases.

**When Cases Arrive:**
- AI ethics score is borderline (5-7 range)
- Community evaluators are split
- Request is edge case (unusual scenario)
- Potential harm detected but unclear

**What You See:**
- Request content
- AI scores (legality, morality, harm, cultural impact)
- Number of community evaluations
- Reason it needs human review

**Actions:**
- **Approve** → Request moves forward, can be fulfilled
- **Reject** → Request is blocked permanently
- **Request More Info** → Ask submitter to clarify

**Why This Matters:**
This is the moral compass. The system can handle clear cases (legal/illegal, moral/immoral). But gray areas need human judgment. That's you.

---

### 3. TASK ARBITRATION

**Purpose:** Resolve stuck fulfillment tasks.

**When Tasks Arrive:**
- System can't find matches (no contributions fit request)
- Multiple conflicts (too many competing offers)
- Fulfillment stuck (contributor ghosted, shipping failed)
- Errors in process (payment failed, coordination broke)

**What You See:**
- Request details
- Issue type (no_matches, conflicts, stuck, error)
- Description of problem
- Suggested actions (from system)

**Actions:**
- Manual match (connect request with specific contribution)
- Escalate to company sponsor
- Mark as unfulfillable (explain why)
- Override system decision

---

### 4. CONTROLLER MANAGEMENT

**Purpose:** Appoint trusted people to help you manage the system.

**Who Are Controllers?**
- Trusted individuals who assist with Black Box duties
- Can have limited permissions (not full master access)
- Example: Security expert handles code review, ethicist handles ethics

**Permissions:**
- `code_review` - Can review and approve code
- `ethics_review` - Can decide ethics cases
- `task_arbitration` - Can resolve stuck tasks
- `all` - Full access (only for master)

**How to Add Controller:**
1. Go to "Controllers" tab
2. Enter: Name, Email, Permissions
3. System generates unique access key
4. Send key to controller securely (encrypted email, Signal, etc.)
5. They can now access Black Box with their key

**How to Revoke:**
1. Find controller in list
2. Click "Revoke"
3. Their key is immediately invalid
4. Logged in audit trail

---

### 5. DASHBOARD METRICS

**Real-time System Health:**

- **Code Review:** Pending / Approved / Rejected submissions
- **Ethics:** Pending / Decided cases
- **Tasks:** Arbitrations needed
- **Platform:** Total users, total requests

**Use This To:**
- Monitor workload (if 100+ pending code reviews, you need more controllers)
- Spot patterns (if lots of ethics cases rejected, tighten submission guidelines)
- Track growth (user numbers increasing)

---

### 6. AUDIT LOGS

**Every Black Box action is logged:**

- Who did what
- When they did it
- What they changed
- Why (if provided)

**Example Logs:**
- "master_admin approved code submission abc123"
- "controller_jane rejected ethics case xyz456 - reason: illegal content"
- "master_admin revoked controller_bob access"

**Why This Matters:**
- Accountability (controllers can't act without record)
- Debugging (trace what happened when something breaks)
- Security (detect if controller account compromised)

**Access:** Only master admin can view full audit logs.

---

### 7. EMERGENCY CONTROLS

**System Override:**
Manually override any system decision. Use sparingly.

**Emergency Disable:**
**NUCLEAR OPTION** - Shuts down entire platform immediately.

Use only if:
- Platform is compromised
- Malicious code got through
- Legal/safety emergency
- Catastrophic bug

**Effect:**
- All public pages show "Maintenance Mode"
- No new submissions accepted
- Existing users can't access
- Black Box still accessible (so you can fix issues)

**How to Re-enable:**
- Fix issue
- Remove disable flag from database
- Platform comes back online

---

## Security Best Practices

### Protect Your Master Key

1. **NEVER commit to git** (it's in .env, which is .gitignored, but check)
2. **NEVER share** (not even with controllers - they get their own keys)
3. **Store securely** (password manager like 1Password, Bitwarden)
4. **Rotate monthly** (generate new key, update .env, restart backend)
5. **Use 2FA** (add IP whitelist in production)

### Controller Trust

1. **Only appoint people you deeply trust**
2. **Start with limited permissions** (expand if they prove reliable)
3. **Review their actions** (check audit logs weekly)
4. **Revoke immediately if suspicious** (better safe than sorry)

### Code Review

1. **Don't approve code you don't understand**
2. **Trust the AI review but verify yourself**
3. **If security score < 60, investigate thoroughly**
4. **Watch for obfuscation** (intentionally hard-to-read code)
5. **Check for hidden functionality** (code that does more than claimed)

### Ethics

1. **When in doubt, request more info** (don't guess)
2. **Document your reasoning** (helps future decisions)
3. **Be consistent** (similar cases should get similar decisions)
4. **Consider precedent** (what message does this decision send?)

---

## Common Scenarios

### Scenario 1: Suspicious Code Submission

**Code arrives with:**
- Security score: 40/100
- Issues: "Use of eval()", "Base64 decode", "External HTTP request"
- AI Review: "Code appears to download and execute remote script"

**What To Do:**
1. **Reject immediately**
2. Add comment: "Security violation - remote code execution attempt"
3. Check if same contributor has other submissions (might be malicious actor)
4. Consider banning contributor

---

### Scenario 2: Split Ethics Case

**Request:** "I need help hacking my ex's Facebook account to get my photos back"

**Scores:**
- AI Legality: 2/10 (very illegal)
- AI Morality: 4/10 (understandable motive, illegal method)
- AI Harm: 8/10 (privacy violation)
- Community: 3 approve, 3 reject (split)

**What To Do:**
1. **Reject**
2. Rationale: "While recovering personal photos is understandable, unauthorized account access is illegal and violates privacy. Suggest legal alternatives: contact Facebook support, lawyer for legal recovery."
3. This sets precedent: No illegal methods, even for sympathetic causes

---

### Scenario 3: Stuck Task

**Request:** "I need a laptop for learning to code"

**Issue:** 3 companies offered to donate laptops, all want shipping reimbursement ($50-100)

**Problem:** Requester is broke (that's why they need the laptop)

**What To Do:**
1. **Manual intervention**
2. Contact company with lowest shipping cost
3. Offer: AU4A covers shipping if they donate laptop
4. If no company agrees, mark as "partially fulfillable" and explain to requester
5. OR: Launch campaign to raise shipping funds from community

---

## Database Collections (For Black Box)

**Created automatically on first use:**

- `blackbox_controllers` - Controller accounts
- `blackbox_code_submissions` - Code review queue
- `blackbox_ethics_cases` - Ethics arbitration queue
- `blackbox_task_arbitrations` - Stuck tasks
- `blackbox_audit_logs` - Full audit trail

**DO NOT modify these directly.** Always use Black Box interface.

---

## API Endpoints (For Integration)

**Base:** `/blackbox/`

**Authentication:** Header: `X-Blackbox-Key: <your_key>`

### Controllers
- `POST /blackbox/controllers` - Create controller
- `GET /blackbox/controllers` - List controllers
- `DELETE /blackbox/controllers/{id}` - Revoke controller

### Code Review
- `POST /blackbox/code-submissions` - Submit code for review
- `GET /blackbox/code-submissions` - List submissions
- `PATCH /blackbox/code-submissions/{id}` - Review decision

### Ethics
- `GET /blackbox/ethics-cases` - List ethics cases
- `PATCH /blackbox/ethics-cases/{id}` - Make decision

### Tasks
- `GET /blackbox/task-arbitrations` - List stuck tasks
- `PATCH /blackbox/task-arbitrations/{id}` - Resolve task

### System
- `POST /blackbox/system/override` - Manual override
- `POST /blackbox/system/emergency-disable` - Kill switch
- `GET /blackbox/dashboard` - Metrics
- `GET /blackbox/audit-logs` - View logs

---

## CI/CD Integration (Auto Code Review)

**On every pull request:**

1. GitHub Action triggers
2. Sends code diff to `/blackbox/code-submissions`
3. Automated analysis runs
4. Code appears in your queue
5. You approve/reject
6. If approved, GitHub merges automatically
7. If rejected, PR is closed with your comments

**Setup:** (Add to `.github/workflows/code-review.yml`)

```yaml
name: Black Box Code Review

on:
  pull_request:
    branches: [main]

jobs:
  submit-for-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Submit to Black Box
        run: |
          curl -X POST https://askus4anything.com/blackbox/code-submissions \
            -H "X-Blackbox-Key: ${{ secrets.BLACKBOX_AUTOMATION_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{
              "contributor_github": "${{ github.actor }}",
              "pr_number": ${{ github.event.pull_request.number }},
              "files_changed": ["..."],
              "code_diff": "..."
            }'
```

---

## Troubleshooting

**Problem:** Can't log in to Black Box

**Solution:**
1. Check master key is correct (no extra spaces)
2. Check backend is running (`sudo supervisorctl status backend`)
3. Check backend logs: `tail -100 /var/log/supervisor/backend.err.log`
4. Verify key in .env: `cat /app/backend/.env | grep BLACKBOX_MASTER_KEY`

---

**Problem:** Code review not showing submissions

**Solution:**
1. Check database: `db.blackbox_code_submissions.find().pretty()`
2. Verify CI/CD is sending submissions
3. Check filter (might be looking at "approved" instead of "pending")

---

**Problem:** Controller can't access certain features

**Solution:**
1. Check their permissions: `db.blackbox_controllers.findOne({id: "controller_id"})`
2. Verify they're using correct key
3. Check if still active: `is_active: true`

---

## Master Key Rotation (Monthly Recommended)

**Steps:**

1. **Generate new key:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

2. **Update .env:**
   ```bash
   nano /app/backend/.env
   # Replace old BLACKBOX_MASTER_KEY with new one
   ```

3. **Restart backend:**
   ```bash
   sudo supervisorctl restart backend
   ```

4. **Test with new key:**
   - Navigate to /blackbox
   - Use new key to login
   - Verify access works

5. **Notify controllers:**
   - If they use separate keys, no action needed
   - If anyone has old master key, it's now invalid

---

## The Hidden Nature of The Black Box

**Why It's Hidden:**

1. **Security through obscurity** (attackers can't hack what they don't know exists)
2. **Prevents social engineering** (users can't beg you to approve their stuff if they don't know you exist)
3. **Maintains mystery** (part of progressive revelation - most users never know the control layer exists)
4. **Protects you** (being publicly known as the decision-maker makes you a target)

**Who Knows About It:**

- You (master admin)
- Controllers you appoint
- Core technical team (if any)
- **NO ONE ELSE**

**Keep It That Way.**

---

**The Black Box is the nervous system of AU4A. Protect it. Use it wisely. The integrity of the entire experiment depends on it.**

---

Last updated: 2026-04-08
