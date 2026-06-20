FROM python:3.12-slim

WORKDIR /app

COPY frontend/api/requirements.txt .
COPY agent/ agent/
COPY frontend/api/ frontend/api/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "frontend.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
