FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Add UbuntuGIS PPA for latest GDAL
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:ubuntugis/ppa

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
    libspatialindex-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    libgeos-dev \
    libgeos++-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Get GDAL version and set environment variables
RUN export GDAL_VERSION=$(gdal-config --version) && \
    export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
    export C_INCLUDE_PATH=/usr/include/gdal && \
    export GDAL_LIBRARY_PATH=$(gdal-config --prefix)/lib/libgdal.so && \
    echo "GDAL_VERSION=${GDAL_VERSION}" >> /etc/environment && \
    echo "CPLUS_INCLUDE_PATH=${CPLUS_INCLUDE_PATH}" >> /etc/environment && \
    echo "C_INCLUDE_PATH=${C_INCLUDE_PATH}" >> /etc/environment && \
    echo "GDAL_LIBRARY_PATH=${GDAL_LIBRARY_PATH}" >> /etc/environment

# Create virtual environment
RUN python3.9 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Install GDAL with system version
RUN export GDAL_VERSION=$(gdal-config --version) && \
    pip install --no-cache-dir GDAL==${GDAL_VERSION}

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install requirements with better error reporting
RUN pip install --no-cache-dir -r requirements.txt || (echo "Failed to install requirements" && cat /root/.cache/pip/log/*/log && exit 1)

# Copy project
COPY . .

# Make manage.py executable
RUN chmod +x manage.py

# Expose port
EXPOSE 8090

# Run the application
CMD ["python3.9", "manage.py", "runserver", "0.0.0.0:8090"] 