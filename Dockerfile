FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY src ./src

RUN pip install --no-cache-dir -r src/requirements.txt

CMD echo "Welcome to the RESTgym Docker image. Please use the restgym.sh script to run this image."