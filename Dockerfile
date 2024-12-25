FROM python:3.8-slim

RUN apt update && \
    apt-get install -y libzbar0

WORKDIR /code-generator

COPY app/ /code-generator/app/

RUN pip install --no-cache-dir Pillow python-barcode qrcode fastapi requests "uvicorn[standard]" jinja2 pyzbar python-multipart

ENV APP_PORT=8081

WORKDIR /code-generator/app/

CMD uvicorn main:app --host 0.0.0.0 --port $APP_PORT --forwarded-allow-ips=*