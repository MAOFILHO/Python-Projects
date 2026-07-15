# Build context assumption: build with `docker build -f services/history-service/Dockerfile .`
# from the microservices-lab/ repo root (needed so services/common is in context).
FROM python:3.12-slim
WORKDIR /app

COPY services/common /tmp/common
RUN pip install --no-cache-dir /tmp/common

COPY services/history-service/pyproject.toml ./pyproject.toml
COPY services/history-service/app ./app
RUN pip install --no-cache-dir .

EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
