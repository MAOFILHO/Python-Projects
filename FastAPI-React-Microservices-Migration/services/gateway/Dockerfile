# For future Azure use only - do NOT build/run this locally. No local Docker
# is used in this project; local dev runs every service as a plain uvicorn
# process (see scripts/run_local.py).
#
# Build context assumption: build with `docker build -f services/gateway/Dockerfile .`
# from the microservices-lab/ repo root (needed so both services/common and
# frontend/ are in context).

# ---- Stage 1: build the frontend ----
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: gateway runtime ----
FROM python:3.12-slim
WORKDIR /app

COPY services/common /tmp/common
RUN pip install --no-cache-dir /tmp/common

COPY services/gateway/pyproject.toml ./pyproject.toml
COPY services/gateway/app ./app
RUN pip install --no-cache-dir .

COPY --from=frontend-build /frontend/dist ./static

ENV STATIC_DIR=/app/static

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
