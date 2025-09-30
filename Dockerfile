# Voice AI agent deployment image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for Python audio processing and the Node frontend
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ffmpeg \
        libportaudio2 \
        portaudio19-dev \
        nodejs \
        npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Node dependencies
COPY package.json package-lock.json ./
RUN npm install --production

# Copy the application source
COPY . .

RUN chmod +x startup.sh

EXPOSE 3000

CMD ["./startup.sh"]
