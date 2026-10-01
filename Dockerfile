# LMArenaBridge on Railway
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git curl libnss3 libnspr4 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone --depth 1 https://github.com/CloudWaddie/LMArenaBridge .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir camoufox playwright
RUN camoufox fetch
COPY patches/ /tmp/patches/
RUN python /tmp/patches/apply.py
ENV PORT=8000
EXPOSE 8000
CMD python -m src.main --port $PORT --host 0.0.0.0
