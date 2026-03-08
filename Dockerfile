# Use official Python lightweight base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for psycopg2 and kaleido
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
# Note: Since we don't have a requirements.txt, I'll generate one in the next tool call 
# or use the known dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run the app
ENTRYPOINT ["streamlit", "run", "pg_bot.py", "--server.port=8501", "--server.address=0.0.0.0"]
