# Stage 1: Builder
FROM python:3-alpine AS builder

WORKDIR /build
COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final Image
FROM python:3-alpine

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

COPY --from=builder /install /usr/local

COPY app/. .
COPY config /config
COPY scripts /scripts

CMD [ "python", "main.py" ]