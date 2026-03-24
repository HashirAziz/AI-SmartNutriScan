# ── Base Image ──
FROM python:3.11-slim

# ── Environment Variables ──
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# ── Set Working Directory ──
WORKDIR /app

# ── Install System Dependencies ──
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Copy Requirements First (layer caching) ──
COPY requirements.txt .

# ── Install Python Dependencies ──
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copy Project Files ──
COPY . .

# ── Create Required Directories ──
RUN mkdir -p static/uploads .cache/huggingface

# ── Expose Port ──
EXPOSE 5000

# ── Run App ──
CMD ["python", "app.py"]