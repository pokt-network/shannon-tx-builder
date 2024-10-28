FROM python:3.11.9-slim

WORKDIR /app

# Install necessary build tools and dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    python3-dev \
    pip \
    bash \
    zlib1g-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

ADD . .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV POCKET_ENV=localnet
ENV POKTROLLD_HOME=./localnet/poktrolld

ENTRYPOINT ["python", "-m", "streamlit", "run", "app.py"]
