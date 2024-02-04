from typing import Union
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from io import BytesIO
from PIL import Image, ImageOps
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *
import qrcode,requests

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test")
async def get_qrcode():
    url_1 = 'https://logos-marques.com/wp-content/uploads/2020/09/Logo-Instagram-1-500x281.png'
    url_2 = 'https://logos-marques.com/wp-content/uploads/2021/10/meta_logo-500x250.png'
    url_3 = 'https://logos-marques.com/wp-content/uploads/2021/03/Uber-Eats-Logo-500x283.png'
    image_data = generate_qrcode('Stephane', None, None, None, url_1)
    if image_data:
        return Response(content=image_data, media_type="image/png")
    else:
        raise HTTPException(status_code=400, detail="Error when generating qr code")

def fit_cover(image, target_size):

    original_width, original_height = image.size
    aspect_ratio = original_width / original_height
    target_width, target_height = target_size
    if aspect_ratio > target_width / target_height:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        new_width = int(target_height * aspect_ratio)
        new_height = target_height
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image

def process_resize_image(image_url, target_size=(50, 50), border_size=2, border_color="white"):
    image_response = requests.get(image_url)
    original_image = Image.open(BytesIO(image_response.content))

    # Get the original image dimensions
    original_width, original_height = original_image.size

    # Calculate the aspect ratio
    aspect_ratio = original_width / original_height

    # Calculate the target dimensions with cover approach
    target_width, target_height = target_size
    target_aspect_ratio = target_width / target_height

    if aspect_ratio > target_aspect_ratio:
        new_width = int(target_height * aspect_ratio)
        resized_image = original_image.resize((new_width, target_height), Image.LANCZOS)
        left_margin = (new_width - target_width) // 2
        resized_image = resized_image.crop((left_margin, 0, left_margin + target_width, target_height))
    else:
        new_height = int(target_width / aspect_ratio)
        resized_image = original_image.resize((target_width, new_height), Image.LANCZOS)
        top_margin = (new_height - target_height) // 2
        resized_image = resized_image.crop((0, top_margin, target_width, top_margin + target_height))

    resized_image_with_border = ImageOps.expand(resized_image, border=border_size, fill=border_color)
    return resized_image_with_border



def generate_qrcode(data, qr_color='#000000', background_color='#ffffff', style_point='square', image_url=None):
    qr_color = qr_color or '#000000'
    background_color = background_color or '#ffffff'
    style_point = style_point or 'square'

    logo = None
    if image_url:
        logo = process_resize_image(image_url)
        logo = logo.resize((50, int((50 / float(logo.size[0])) * float(logo.size[1]))), Image.LANCZOS)
        background = Image.new('RGB', logo.size, 'white')
        background.paste(logo, (0, 0), logo)
        logo = background
        
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,   
    )
    
    QRcode.add_data(data)
    QRcode.make()

    module_drawer = None
    style_point_mapping = {
        'square': SquareModuleDrawer(),
        'gapped_square': GappedSquareModuleDrawer(),
        'circle': CircleModuleDrawer(),
        'rounded': RoundedModuleDrawer(),
        'vertical_bar': VerticalBarsDrawer(),
        'horizontal_bar': HorizontalBarsDrawer()
    }
    module_drawer = style_point_mapping.get(style_point, SquareModuleDrawer())

    QRimg = QRcode.make_image(
        version=40,
        fill_color=qr_color, 
        back_color=background_color,
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
    ).convert('RGB')
    
    if logo:
        pos = (
            (QRimg.size[0] - logo.size[0]) // 2,
            (QRimg.size[1] - logo.size[1]) // 2
        )
        QRimg.paste(logo, pos)
    
    img_bytes = BytesIO()
    QRimg.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


