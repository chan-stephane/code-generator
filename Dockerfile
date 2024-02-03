FROM python:3.8-slim

WORKDIR /app

#install of dependencies
RUN pip install "qrcode[pil]" fastapi python-dotenv requests "uvicorn[standard]"
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# uvicorn app.main:app --host 0.0.0.0 --port 80