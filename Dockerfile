FROM python:3.8-slim

WORKDIR /qr-code-generator

#install of dependencies
RUN pip install Pillow image_sizer qrcode fastapi python-dotenv requests "uvicorn[standard]"

ENV APP_PORT=80


# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$APP_PORT"]
# uvicorn app.main:app --host 0.0.0.0 --port 80