FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies and GDAL
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_VERSION=3.6.2

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make manage.py executable
RUN chmod +x manage.py

# Expose port
EXPOSE 8090

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8090"] 