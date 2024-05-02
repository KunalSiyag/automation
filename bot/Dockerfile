FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV WORKSPACE=/workspace

# Copy requirements and install Python dependencies
COPY bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent and API scripts
COPY bot/agent.py ./agent.py
COPY bot/api.py ./api.py
COPY bot/api_v2.py ./api_v2.py
COPY bot/start.sh ./start.sh

# Create workspace mount point
RUN mkdir -p /workspace

# Expose API port
EXPOSE 18789

# Run both agent and API
ENTRYPOINT ["/app/start.sh"]
