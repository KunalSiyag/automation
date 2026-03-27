FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent and API scripts
COPY agent.py .
COPY api.py .
COPY api_v2.py .

# Create workspace mount point
RUN mkdir -p /workspace

# Expose API port
EXPOSE 18789

# Create entrypoint script to run both agent and API
RUN echo '#!/bin/bash\npython -u agent.py &\nPIDOF_AGENT=$!\nsleep 2\npython -u api_v2.py\nkill $PIDOF_AGENT 2>/dev/null || true' > /app/start.sh && chmod +x /app/start.sh

# Run both agent and API
ENTRYPOINT ["/app/start.sh"]
