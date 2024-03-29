FROM python:3.8-alpine

WORKDIR /code-generator

COPY app/ /code-generator/app/

RUN pip install --no-cache-dir Pillow python-barcode qrcode fastapi requests "uvicorn[standard]"

ENV APP_PORT=8080

#CMD uvicorn app.main:app --host 0.0.0.0 --port $APP_PORT

