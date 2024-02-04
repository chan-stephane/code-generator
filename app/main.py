from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
from .code_generator import generate_qrcode, generate_barcode
from io import BytesIO


class QRCodeRequest(BaseModel):
    data: str = 'Some data'
    color: Optional[str] = '#000000'
    bg_color: Optional[str] = '#ffffff'
    style_points: Optional[str] = 'square'
    image_url: Optional[str] = ''


class BARCodeRequest(BaseModel):
    data: str = 'Some data'

app = FastAPI()


@app.post("/qr-code/generate")
async def generate_qrcode_endpoint(request: QRCodeRequest):
    try:
        qr_code_data = generate_qrcode(request.data, request.color, request.bg_color, request.style_points, request.image_url)
        return StreamingResponse(BytesIO(qr_code_data), media_type="image/png")
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)


@app.post("/bar-code/generate")
async def generate_barcode_endpoint(request: BARCodeRequest):
    try:
        bar_code_data = generate_barcode(request.data)
        return StreamingResponse(BytesIO(bar_code_data), media_type="image/png")
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)


