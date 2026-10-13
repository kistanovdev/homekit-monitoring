FROM python:3.13-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping iputils-arping \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hkmon ./hkmon
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "hkmon"]
