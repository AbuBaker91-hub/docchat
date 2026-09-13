FROM python:3.12-slim

WORKDIR /srv/docchat

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# CPU-only torch first (much smaller than the CUDA default), then the app with
# the real-embeddings extra so the image answers with real MiniLM vectors.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir ".[demo]"

EXPOSE 8000
CMD ["python", "scripts/start.py"]
