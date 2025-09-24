FROM python:3.11-slim
RUN apt-get update && apt-get install -y tcpdump libpcap0.8 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
# Expose API port (matches PSN_PORT)
EXPOSE 8088
# Run API and sniffer via supervisord (simple) — for brevity use bash to start both
CMD bash -lc "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PSN_PORT:-8088} & \
              python sniffer/sniffer.py"
