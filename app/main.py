from typing import Union
from fastapi import FastAPI
from fastapi.responses import Response
import qrcode
from io import BytesIO
import PIL.Image

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test")
async def get_qrcode():
    return generate_qrcode()

@app.get("/image")
async def read_image():
    image_path = "./app/man.png"
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    return Response(content=image_data, media_type="image/png")

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

def generate_qrcode():
    data = "GeeksforGeeks"
    qr = qrcode.QRCode(version = 1,
                    box_size = 10,
                    border = 5)
    qr.add_data(data)
    qr.make(fit = True)
    img = qr.make_image(fill_color = 'red',
                        back_color = 'white')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    image_data = img_bytes.getvalue()
    return Response(content=image_data, media_type="image/png")

