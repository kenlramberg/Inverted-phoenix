# AU4A - Ask Us 4 Anything

> "Do you want the answers 2 everything...?"

## The Greatest Social Experiment in History

AU4A is a human-powered, AI-assisted system designed to fulfill requests through goodwill, collaboration, and ethical coordination.

It is:
- A digital wishing well
- A search engine of truth
- A social experiment

It is **not**:
- A business
- An ad platform
- A transactional system

It is built on **contribution, not extraction**.

---

## Philosophy

Knowledge is freedom. When used with positive intention, knowledge improves humanity.

AU4A is designed to:
- Encourage giving
- Fulfill needs ethically
- Coordinate human goodwill
- Remove monetary influence from outcomes

---

## The 4 Parts System

The platform operates through four interconnected layers (revealed gradually through participation):

### A — Ask
Submit wishes, questions, needs, or problems. Ethical and legal only.

### B — Contribute (Borrow / Barter / Buy / Bring / Bestow / Befriend)
Participate by helping fulfill requests through various forms of giving.

### C — Coordinate (Cooperate / Collaborate)
Strategize and organize how to fulfill complex requests.

### D — Execute (Dedicate / Demonstrate / Donate / Deploy)
Take action and make wishes real.

---

## Tech Stack

**Backend:**
- FastAPI (Python)
- MongoDB (Database)
- Motor (Async MongoDB driver)

**Frontend:**
- React 19
- React Router
- Tailwind CSS
- shadcn/ui components
- Axios

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Yarn

### Installation

1. **Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Frontend Setup:**
```bash
cd frontend
yarn install
```

3. **Environment Variables:**

Create `.env` files in both `backend/` and `frontend/` directories.

**Backend `.env`:**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=au4a
CORS_ORIGINS=http://localhost:3000
```

**Frontend `.env`:**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Running the Application

**Backend:**
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```bash
cd frontend
yarn start
```

The application will be available at `http://localhost:3000`

---

## API Documentation

### Core Endpoints

#### Ask Layer
- `POST /api/ask` - Submit a request
- `GET /api/requests` - Browse requests (with filters)
- `GET /api/request/{id}` - Get single request details

#### Ethics Engine
- `POST /api/evaluate` - Submit ethical evaluation
- `GET /api/evaluate/pending` - Get requests needing evaluation
- `GET /api/evaluate/{request_id}` - Get evaluations for a request

#### Contribute Layer
- `POST /api/contribute` - Submit contribution
- `GET /api/contributions/{request_id}` - Get contributions for request

#### Coordinate Layer
- `POST /api/coordinate` - Create coordination task
- `GET /api/coordinate/{request_id}` - Get coordination tasks

#### Execute Layer
- `POST /api/execute` - Log execution action
- `GET /api/execute/{request_id}` - Get execution history

#### Search
- `GET /api/search?q=query` - Search knowledge base

#### User Progress
- `GET /api/user/{user_id}/progress` - Get participation level
- `GET /api/user/{user_id}/stats` - Get user statistics

---

## Features

### ✅ Implemented

- **Ask System**: Submit requests with categorization
- **Ethics Evaluation Engine**: Distributed human polling for legality, morality, harm potential
- **Contribution System**: Multiple ways to help (borrow/barter/buy/bring/bestow/befriend)
- **Coordination Workspace**: Plan and strategize fulfillment
- **Execution Tracking**: Log actions and verify completion
- **Search Engine**: Human-curated knowledge base (no external APIs)
- **Progressive Revelation**: Features unlock through participation
- **User Journey Tracking**: Participation levels and unlocked features

### 🔄 Core Principles

- **No ads** - Ever
- **No paid ranking** - Truth-based search
- **No monetized influence** - Pure goodwill
- **No extraction** - Contribution-based
- **Ethical by design** - Community-driven moral compass

---

## Progressive Revelation System

**The 4 quadrants reveal SEQUENTIALLY and COMPULSORILY** - not all at once. Users must complete each part before the next is revealed.

### Sequential Revelation:

| Actions Completed | Visible Quadrant | Required Action |
|-------------------|------------------|-----------------|
| 0 | **Ask** only | Submit a request |
| 1+ | **Ask** + **Contribute** | Help fulfill a request |
| 3+ | **Ask** + **Contribute** + **Coordinate** | Create coordination plan |
| 5+ | **All 4 Quadrants** | Execute an action |

**This is compulsory, not a choice.** You cannot skip to the next quadrant without completing the previous one.

---

## Ethics Engine

Every request is evaluated for:
- **Legality** (1-10 scale)
- **Morality** (1-10 scale)
- **Harm Potential** (1-10 scale, higher = more harmful)
- **Cultural Impact** (1-10 scale)

Requests require multiple evaluations before approval. Auto-rejection occurs for:
- Harm score > 7
- Legality score < 4
- Morality score < 4

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

### Core Rules
- No external search engine APIs
- No scraping other search engines
- No ads (ever)
- No paid ranking influence

---

## Project Structure

```
/app
├── backend/
│   ├── server.py          # Main FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages (Landing, Ask, Evaluate, etc.)
│   │   ├── components/   # UI components
│   │   ├── App.js        # Main React component
│   │   └── index.js      # Entry point
│   ├── package.json      # Node dependencies
│   └── .env             # Frontend environment variables
└── inverted-phoenix/     # GitHub seed project
    ├── README.md
    └── CONTRIBUTING.md
```

---

## License

MIT License - See LICENSE file for details

---

## The Vision

> Something is being built here. Not a company. Not a product. Not a platform in the usual sense.

> It doesn't sell. It doesn't rank by money. It doesn't belong to anyone.

> **It belongs to us.**

---

**AU4A - Built on contribution, not extraction.**
