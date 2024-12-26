FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-venv \
    python3-pip \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3.9 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make manage.py executable
RUN chmod +x manage.py

# Expose port
EXPOSE 8090

# Run the application
CMD ["python3.9", "manage.py", "runserver", "0.0.0.0:8090"] 