from typing import Optional
from fastapi import FastAPI, Query, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import quote, unquote
from fastapi.responses import StreamingResponse, JSONResponse
from code_generator import generate_qrcode, generate_qrcode_download, generate_barcode
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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def is_not_encoded(data):
    try:
        decoded_data = unquote(data)
        return decoded_data == data
    except Exception:
        return False


def handleErrorEncoded(msg):
    return JSONResponse(content={"error": msg}, status_code=400)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.get("/up")
def welcome(request: Request):
    return JSONResponse(content={"message": "Code generator is working successfully, go to {}docs to test".format(request.url)}, status_code=200)


@app.get("/qr-code")
async def on_demand_qr_code(
    data: str = Query('Some data')
):
    try:
        color ='#000000'
        bg_color = '#ffffff'
        style_points = 'square'
        image_url = ''
        if is_not_encoded(data): 
            qr_code_data = generate_qrcode(data, color, bg_color, style_points, image_url)
            return StreamingResponse(BytesIO(qr_code_data), media_type="image/png")
        else:
            return handleErrorEncoded('field data should be encoded')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/qr-code/generate")
async def generate_qrcode_endpoint(request: QRCodeRequest):
    try:
        qr_code_data = generate_qrcode(request.data, request.color, request.bg_color, request.style_points, request.image_url)
        return StreamingResponse(BytesIO(qr_code_data), media_type="image/png")
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)


@app.post("/qr-code/download")
async def generate_qrcode_download_endpoint(request: QRCodeRequest):
    try:
        qr_code_data = generate_qrcode_download(request.data, request.color, request.bg_color, request.style_points, request.image_url)
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


