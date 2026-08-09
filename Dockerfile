# Atlas AI Financial Assistant - Multi-Stage Container
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend/
COPY README.md ./

ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE 8000

# Start unified FastAPI server and Telegram bot daemon
CMD ["python", "backend/main.py"]
