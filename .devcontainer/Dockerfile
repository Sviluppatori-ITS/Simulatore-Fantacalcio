FROM python:3.13-slim

# Sicurezza e tool base + nodejs
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git curl gnupg2 ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

CMD ["bash"]
