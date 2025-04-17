FROM python:3.10-alpine

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
# Add build dependencies for any compiled packages, then remove them after pip install
RUN apk add --no-cache --virtual .build-deps gcc musl-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del .build-deps

# Copy application code
COPY plex_monitor.py .
COPY config.template.json .

# Create volume mount points
VOLUME ["/app/config", "/app/logs"]

# Set environment variables
ENV CONFIG_PATH=/app/config/config.json
ENV LOG_PATH=/app/logs/plex_monitor.log

# Create a non-root user to run the application
RUN adduser -D appuser
RUN chown -R appuser:appuser /app
USER appuser

# Modify the script to use environment variables for config and log paths
RUN sed -i 's|CONFIG_FILE = '\''config.json'\''|CONFIG_FILE = os.environ.get("CONFIG_PATH", "config.json")|' plex_monitor.py && \
    sed -i 's|LOG_FILE = '\''plex_monitor.log'\''|LOG_FILE = os.environ.get("LOG_PATH", "plex_monitor.log")|' plex_monitor.py

# Handle signals properly
STOPSIGNAL SIGTERM

# Run the application
CMD ["python", "-u", "plex_monitor.py"]
