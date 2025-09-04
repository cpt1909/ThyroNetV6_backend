# Stage 1: Build with dependencies
FROM python:3.11-slim AS builder

WORKDIR /backend

# Install system deps required by PyTorch + vision libs
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install CPU-only PyTorch + other deps
RUN pip install --no-cache-dir gunicorn \
    && pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /backend

# Install only required system libs (no build tools)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python packages and app from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /backend /backend

# Expose Flask/Gunicorn port
EXPOSE 5000

# Run Flask app with Gunicorn (4 workers, auto-tuned threads)
CMD ["gunicorn", "--workers=4", "--threads=2", "--bind=0.0.0.0:5000", "app:app"]
