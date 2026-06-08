# Digiorg

A persistent digital organism with an autonomous vital cycle, hybrid directive system, local LLM reasoning and a real-time dashboard.

## What is Digiorg?

Digiorg is a digital organism that lives, makes decisions and evolves autonomously. It has vital stats (energy, hunger, sleepiness, hygiene), a decision engine that combines deterministic logic with local LLM reasoning (Ollama), persistent memory and a real-time web dashboard.

## Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy, SQLite
- **LLM:** Ollama (local, no external dependencies)
- **Frontend:** React + Vite + Recharts
- **Communication:** Real-time WebSocket

## Requirements

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Rokhen/Digiorg.git
cd Digiorg

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -e .

# 4. Install LLM model
ollama pull llama3.1:8b

# 5. Install frontend dependencies
cd frontend
npm install
cd ..
```

## Quick start with Docker

```bash
docker compose up
```

Open your browser at `http://localhost`.

## Development mode

**Terminal 1 — Backend:**
```bash
uvicorn src.interface.api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open your browser at `http://localhost:5173`.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/state` | GET | Full vital state |
| `/body` | GET | Avatar and physical descriptor |
| `/brain` | GET | On-demand LLM reasoning |
| `/sensors` | GET | System metrics (CPU, RAM, disk) |
| `/safety` | GET | System limits validation |
| `/events` | GET | Event history |
| `/memory/snapshots` | GET | State history |
| `/memory/patterns` | GET | Stat trends |
| `/action/feed` | POST | Feed Digiorg |
| `/action/sleep` | POST | Put to sleep |
| `/action/clean` | POST | Clean |
| `/action/revive` | POST | Revive |
| `/directives` | GET/POST | List and create directives |
| `/directives/{name}` | PATCH/DELETE | Activate, deactivate or delete |
| `/scheduler` | GET | Scheduler status |
| `/ws` | WebSocket | Real-time stream |

Interactive documentation available at `http://127.0.0.1:8000/docs`.

## Directive system

Digiorg supports a hybrid directive system with two layers:

**Typed directives** — deterministic, always reliable:
- `sleep` — triggers sleep when sleepiness exceeds threshold
- `hunger` — triggers feeding when hunger exceeds threshold
- `hygiene` — triggers cleaning when hygiene falls below threshold

**Custom directives** — interpreted by the LLM in natural language. Describe any behavior and the LLM will reason about it.

## Configuration

Edit `config/settings.toml` to adjust behavior:

```toml
[life]
tick_seconds = 10          # Vital cycle frequency

[autonomy]
enabled = true             # Enable/disable autonomy
sleep_threshold = 70       # Sleepiness threshold to sleep
hunger_threshold = 70      # Hunger threshold to feed
hygiene_threshold = 40     # Hygiene threshold to clean

[brain]
llm_enabled = true         # Enable/disable LLM
llm_model = "llama3.1:8b" # Ollama model
llm_every_n_ticks = 3      # LLM query frequency

[safety]
max_cpu_percent = 50       # CPU limit
max_memory_mb = 57344      # RAM limit in MB
```

## Tests

```bash
pytest tests/ -v
```

## Project structure

digiorg/
├── config/          # Configuration
├── frontend/        # React dashboard
├── src/
│   ├── body/        # Physical representation and avatar
│   ├── brain/       # Decision engine + LLM
│   ├── core/        # Core: models, state, actions, events
│   ├── interface/   # REST API + WebSocket
│   ├── memory/      # Snapshots and patterns
│   ├── safety/      # System limits
│   ├── scheduler/   # Autonomous tick
│   └── sensors/     # System metrics
└── tests/           # Automated tests
