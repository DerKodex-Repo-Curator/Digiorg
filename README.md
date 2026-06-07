# Digiorg

Organismo digital persistente con ciclo vital autónomo, motor de decisión con LLM local y dashboard en tiempo real.

## ¿Qué es Digiorg?

Digiorg es un organismo digital que vive, toma decisiones y evoluciona de forma autónoma. Tiene stats vitales (energía, hambre, somnolencia, higiene), un motor de decisión que combina lógica determinista con razonamiento LLM local (Ollama), memoria persistente y un dashboard web en tiempo real.

## Stack

- **Backend:** Python 3.10+, FastAPI, SQLAlchemy, SQLite
- **LLM:** Ollama (local, sin dependencias externas)
- **Frontend:** React + Vite + Recharts
- **Comunicación:** WebSocket en tiempo real

## Requisitos

- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) instalado y corriendo

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd digiorg

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias Python
pip install -e .

# 4. Instalar modelo LLM
ollama pull llama3.1:8b

# 5. Instalar dependencias frontend
cd frontend
npm install
cd ..
```

## Arranque

**Terminal 1 — Backend:**
```bash
uvicorn src.interface.api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Abre el navegador en `http://localhost:5173`.

## API

| Endpoint | Método | Descripción |
|---|---|---|
| `/state` | GET | Estado vital completo |
| `/body` | GET | Avatar y descriptor físico |
| `/brain` | GET | Razonamiento LLM bajo demanda |
| `/sensors` | GET | Métricas del sistema (CPU, RAM, disco) |
| `/safety` | GET | Validación de límites del sistema |
| `/events` | GET | Historial de eventos |
| `/memory/snapshots` | GET | Histórico de estados |
| `/memory/patterns` | GET | Tendencias por stat |
| `/action/feed` | POST | Alimentar a Digiorg |
| `/action/sleep` | POST | Dormir |
| `/action/clean` | POST | Limpiar |
| `/action/revive` | POST | Resucitar |
| `/directives` | GET/POST | Listar y crear directivas |
| `/directives/{name}` | PATCH/DELETE | Activar, desactivar o eliminar |
| `/scheduler` | GET | Estado del scheduler |
| `/ws` | WebSocket | Stream en tiempo real |

Documentación interactiva disponible en `http://127.0.0.1:8000/docs`.

## Configuración

Edita `config/settings.toml` para ajustar el comportamiento:

```toml
[life]
tick_seconds = 10          # Frecuencia del ciclo vital

[autonomy]
enabled = true             # Activar/desactivar autonomía
sleep_threshold = 70       # Umbral de somnolencia para dormir
hunger_threshold = 70      # Umbral de hambre para comer
hygiene_threshold = 40     # Umbral de higiene para limpiar

[brain]
llm_enabled = true         # Activar/desactivar LLM
llm_model = "llama3.1:8b" # Modelo Ollama
llm_every_n_ticks = 3      # Frecuencia de consulta al LLM

[safety]
max_cpu_percent = 50       # Límite de CPU
max_memory_mb = 57344      # Límite de RAM en MB
```

## Tests

```bash
pytest tests/ -v
```

## Estructura

```
digiorg/
├── config/          # Configuración
├── frontend/        # Dashboard React
├── src/
│   ├── body/        # Representación física y avatar
│   ├── brain/       # Motor de decisión + LLM
│   ├── core/        # Núcleo: modelos, estado, acciones, eventos
│   ├── interface/   # API REST + WebSocket
│   ├── memory/      # Snapshots y patrones
│   ├── safety/      # Límites del sistema
│   ├── scheduler/   # Tick autónomo
│   └── sensors/     # Métricas del sistema
└── tests/           # Tests automatizados
```