FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps for ffmpeg if users want to stitch videos; lightweight install
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "src.web:app", "--host", "0.0.0.0", "--port", "8000"]
