# Build context assumption: build with `docker build -f services/monolith/Dockerfile .`
# from the microservices-lab/ repo root (needed so services/common is in context).
FROM python:3.12-slim
WORKDIR /app

COPY services/common /tmp/common
RUN pip install --no-cache-dir /tmp/common

COPY services/monolith/pyproject.toml ./pyproject.toml
COPY services/monolith/app ./app
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
