FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Código fuente
COPY config/ config/
COPY src/ src/

# Directorios de datos
RUN mkdir -p data/db data/logs data/state data/memory

EXPOSE 8000

CMD ["uvicorn", "src.interface.api:app", "--host", "0.0.0.0", "--port", "8000"]