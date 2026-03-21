# Use lightweight Python image
FROM python:3.10-slim

# Force rebuild by adding timestamp
ARG BUILDKIT_INLINE_CACHE=1
RUN echo "Build timestamp: $(date)"

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Run app with Python script that handles PORT env var
CMD ["python", "start.py"]