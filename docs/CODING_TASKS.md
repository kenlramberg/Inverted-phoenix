# AU4A Coding Tasks - GitHub Issues

## How to Use This File

Create GitHub issues for each task using the templates below. Developers can browse, claim, and complete tasks.

---

## TASK TEMPLATE

```markdown
### [TASK-XXX] Task Title

**Type:** Quick Win / Medium / Major  
**Estimated Time:** X hours  
**Skills Required:** Python/React/MongoDB/etc.  
**Difficulty:** Beginner / Intermediate / Advanced  

#### Description
Clear explanation of what needs to be done.

#### Current State
What exists now (with file references).

#### Desired State
What it should look like after completion.

#### Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

#### Files to Modify
- `/app/backend/server.py`
- `/app/frontend/src/pages/Example.js`

#### Resources
- [Link to relevant docs]
- [Example implementation]

#### How to Get Started
1. Clone repo
2. Run `npm install` and `pip install -r requirements.txt`
3. Read `/docs/CONTRIBUTING.md`
4. Ask questions in Discord

#### Reward
Early access to AU4A + your name on contributors page.

---

**To claim:** Comment "I'll take this" and we'll assign it to you.
```

---

## ACTUAL TASKS (Ready to Create as Issues)

### Quick Wins (2-3 hours each)

#### TASK-001: Fix Mobile Responsiveness on Ask Page

**Type:** Quick Win  
**Time:** 2-3 hours  
**Skills:** React, Tailwind CSS  
**Difficulty:** Beginner  

**Description:**  
The Ask page doesn't display well on mobile devices (< 640px width). Input fields overflow, buttons are too small, and spacing is off.

**Current State:**  
`/app/frontend/src/pages/Ask.js` has fixed desktop layouts.

**Desired State:**  
Fully responsive on all screen sizes with proper touch targets (minimum 44x44px).

**Acceptance Criteria:**
- [ ] Textarea adjusts width on mobile
- [ ] Buttons are at least 44px tall
- [ ] No horizontal scrolling on any screen size
- [ ] Tested on iPhone and Android (Chrome DevTools)

**Files:**
- `/app/frontend/src/pages/Ask.js`

---

#### TASK-002: Add Loading States to All Buttons

**Type:** Quick Win  
**Time:** 2 hours  
**Skills:** React  
**Difficulty:** Beginner  

**Description:**  
When users click submit buttons, there's no visual feedback while the API call is processing.

**Current State:**  
Buttons just say "Submit" with `disabled` state but no loading indicator.

**Desired State:**  
Buttons show "Loading..." or a spinner icon while processing.

**Acceptance Criteria:**
- [ ] All submit buttons show loading state
- [ ] Loading state appears immediately on click
- [ ] Clears when API response received
- [ ] Disabled during loading

**Files:**
- `/app/frontend/src/pages/Ask.js`
- `/app/frontend/src/pages/Evaluate.js`
- `/app/frontend/src/pages/Contribute.js`
- `/app/frontend/src/pages/WhatCanYouGive.js`

---

#### TASK-003: Improve Error Messages

**Type:** Quick Win  
**Time:** 2-3 hours  
**Skills:** React, UX Writing  
**Difficulty:** Beginner  

**Description:**  
Current error messages are technical ("Error 500", "Failed to fetch"). Make them user-friendly and actionable.

**Current State:**  
Generic error messages from API.

**Desired State:**  
Helpful, human-readable errors with suggested actions.

**Examples:**
- Before: "Error 500"
- After: "Oops! Something went wrong on our end. Please try again in a moment."

- Before: "Failed to fetch"
- After: "We couldn't load that content. Check your internet connection and try again."

**Acceptance Criteria:**
- [ ] All error messages are human-readable
- [ ] Include suggested action when possible
- [ ] Maintain friendly, non-technical tone
- [ ] Tested with various error scenarios

**Files:**
- All `/app/frontend/src/pages/*.js` files

---

### Medium Tasks (4-6 hours each)

#### TASK-010: Build Email Notification System

**Type:** Medium  
**Time:** 4-5 hours  
**Skills:** Python, Email APIs  
**Difficulty:** Intermediate  

**Description:**  
Users should receive emails when:
1. Their request is approved
2. Someone offers to contribute
3. Their wish is fulfilled

**Current State:**  
No email system exists.

**Desired State:**  
Backend sends emails using SendGrid (or similar) for key events.

**Acceptance Criteria:**
- [ ] Email templates created (HTML + plain text)
- [ ] Sends on request approval
- [ ] Sends on new contribution offer
- [ ] Sends on fulfillment
- [ ] Unsubscribe link included
- [ ] Tested with real emails

**Files:**
- Create `/app/backend/notifications.py`
- Modify `/app/backend/server.py` (add hooks)
- Add to `requirements.txt`: `sendgrid` or `resend`

**Resources:**
- [SendGrid Python Docs](https://github.com/sendgrid/sendgrid-python)

---

#### TASK-011: Add Accessibility Features (WCAG 2.1 AA)

**Type:** Medium  
**Time:** 5-6 hours  
**Skills:** React, Accessibility  
**Difficulty:** Intermediate  

**Description:**  
Make AU4A accessible to users with disabilities.

**Current State:**  
No ARIA labels, inconsistent keyboard navigation, poor screen reader support.

**Desired State:**  
WCAG 2.1 AA compliant.

**Acceptance Criteria:**
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels on all form inputs
- [ ] Focus indicators visible
- [ ] Skip-to-content link
- [ ] Color contrast meets AA standards
- [ ] Tested with screen reader (NVDA/VoiceOver)

**Files:**
- All `/app/frontend/src/pages/*.js`
- All `/app/frontend/src/components/ui/*.js`

**Resources:**
- [WCAG 2.1 Checklist](https://www.a11yproject.com/checklist/)
- [React Accessibility Docs](https://react.dev/learn/accessibility)

---

#### TASK-012: Optimize Database Queries

**Type:** Medium  
**Time:** 4-5 hours  
**Skills:** MongoDB, Performance  
**Difficulty:** Intermediate  

**Description:**  
Some API endpoints are slow with large datasets. Add indexes and optimize queries.

**Current State:**  
No indexes except default `_id`. Some queries use `$regex` without indexes.

**Desired State:**  
All frequently-queried fields indexed. Query times < 100ms.

**Acceptance Criteria:**
- [ ] Indexes added to: `requests.status`, `requests.category`, `requests.created_at`
- [ ] Indexes added to: `contribution_offers.is_fulfilled`, `contribution_offers.offer_type`
- [ ] Compound index: `sponsors.display_on_homepage + display_order`
- [ ] Text index on `knowledge_base` for search
- [ ] Query performance tested (load 10,000+ records)
- [ ] Document indexes in `/docs/DATABASE.md`

**Files:**
- `/app/backend/server.py` (add index creation on startup)
- Create `/docs/DATABASE.md`

**Resources:**
- [MongoDB Indexing Best Practices](https://www.mongodb.com/docs/manual/indexes/)

---

### Major Tasks (8+ hours each)

#### TASK-020: Automated Testing Suite

**Type:** Major  
**Time:** 8-10 hours  
**Skills:** Python, pytest, API testing  
**Difficulty:** Advanced  

**Description:**  
Build comprehensive test suite for backend API.

**Current State:**  
No automated tests exist.

**Desired State:**  
50%+ code coverage with pytest.

**Acceptance Criteria:**
- [ ] Unit tests for all API endpoints
- [ ] Integration tests for key workflows
- [ ] Test fixtures for database
- [ ] CI integration (GitHub Actions)
- [ ] Minimum 50% coverage
- [ ] All tests pass

**Files:**
- Create `/app/tests/` directory
- Create `/app/tests/test_api.py`
- Create `/app/tests/conftest.py` (fixtures)
- Create `.github/workflows/test.yml` (CI)

**Resources:**
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

#### TASK-021: Build Analytics Dashboard

**Type:** Major  
**Time:** 6-8 hours  
**Skills:** React, Data Visualization  
**Difficulty:** Intermediate-Advanced  

**Description:**  
Create admin dashboard showing platform metrics (privacy-preserving).

**Current State:**  
No analytics dashboard.

**Desired State:**  
Dashboard showing:
- Total requests, contributions, evaluations
- Fulfillment rate over time
- Category breakdown
- Active users (last 7 days)
- Top contributors

**Acceptance Criteria:**
- [ ] New page `/analytics`
- [ ] Charts using Recharts or similar
- [ ] No individual user tracking (aggregated only)
- [ ] Real-time data (updates on page load)
- [ ] Mobile responsive
- [ ] Export data as CSV

**Files:**
- Create `/app/frontend/src/pages/Analytics.js`
- Add route in `/app/frontend/src/App.js`
- Create `/app/backend/server.py` endpoint: `GET /api/analytics`

**Resources:**
- [Recharts Docs](https://recharts.org/)

---

## How to Create These Issues

1. Go to GitHub repository
2. Click "Issues" → "New Issue"
3. Copy template above
4. Fill in task details
5. Add labels: `good first issue`, `help wanted`, `frontend`, `backend`, etc.
6. Assign to projects/milestones
7. Post in Discord: "New task available!"

---

**Total Tasks Available: 30**  
**Target Completions: 20**  
**Buffer: 10 tasks (50%)**

This ensures even with attrition, we hit our launch goals.
