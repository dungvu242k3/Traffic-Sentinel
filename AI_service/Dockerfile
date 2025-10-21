FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt
COPY ./processing ./processing
COPY ./connectors ./connectors
COPY ./main.py ./main.py
COPY ./models ./models
