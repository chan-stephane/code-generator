from io import BytesIO
from PIL import Image, ImageOps, ImageColor
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *
from barcode.writer import ImageWriter
from fastapi import HTTPException
from base64 import b64encode
from pathlib import Path
from pyzbar.pyzbar import decode
import qrcode,barcode,requests,random


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def is_image_url(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '').lower()
        return content_type.startswith('image/')
    except requests.RequestException as e:
        return False


def resizing_image(img, target_size=(300, 300), border_size=2, border_color="white"):
    original_width, original_height = img.size
    aspect_ratio = original_width / original_height
    target_width, target_height = target_size
    target_aspect_ratio = target_width / target_height
    if aspect_ratio > target_aspect_ratio:
        new_width = int(target_height * aspect_ratio)
        resized_image = img.resize((new_width, target_height), Image.LANCZOS)
        left_margin = (new_width - target_width) // 2
        resized_image = resized_image.crop((left_margin, 0, left_margin + target_width, target_height))
    else:
        new_height = int(target_width / aspect_ratio)
        resized_image = img.resize((target_width, new_height), Image.LANCZOS)
        top_margin = (new_height - target_height) // 2
        resized_image = resized_image.crop((0, top_margin, target_width, top_margin + target_height))

    resized_image_with_border = ImageOps.expand(resized_image, border=border_size, fill=border_color)
    return resized_image_with_border

def generate_qrcode(data, qr_color=None, background_color=None, style_point=None, image_url=None):

    qr_color = '#000000' if qr_color is None else '#000000' if qr_color=='' else qr_color 
    background_color = '#ffffff' if background_color is None else '#ffffff' if background_color=='' else background_color
    style_point = 'square' if style_point is None else 'square' if style_point=='' else style_point
    if background_color == '#000000':
        print('go change color')
        background_color = '#111111'
    valid_style_points = ['square', 'gapped_square', 'circle', 'rounded', 'vertical_bar', 'horizontal_bar']
    if style_point not in valid_style_points:
        raise HTTPException(status_code=400, detail="Invalid style_point")

    logo = None

    if image_url and image_url!='':
        if is_image_url(image_url):
            image_response = requests.get(image_url)
            original_image = Image.open(BytesIO(image_response.content))
            const_w = 50
            new_logo_size = (const_w, (original_image.size[1] * const_w) // original_image.size[0])
            logo = resizing_image(original_image, target_size=new_logo_size)
            logo = logo.convert('RGBA')
            background = Image.new('RGBA', logo.size, hex_to_rgb(background_color) + (255,))
            background.paste(logo, (0, 0), logo)
            logo = background
        else:
            raise HTTPException(status_code=400, detail="Field image_url is not a valid url")

    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        image_factory=StyledPilImage,
        box_size=10,
        border=2,   
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
        module_drawer=module_drawer,
        eye_drawer=module_drawer,
        color_mask=SolidFillColorMask(back_color=hex_to_rgb(background_color),front_color=hex_to_rgb(qr_color)),
    ).convert('RGBA')
    
    if logo:
        pos = (
            (QRimg.size[0] - logo.size[0]) // 2,
            (QRimg.size[1] - logo.size[1]) // 2
        )
        QRimg.paste(logo, pos)
    QRimg = resizing_image(QRimg)
    img_bytes = BytesIO()
    QRimg.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def generate_barcode(data):
    # Create a Code128 barcode
    barcode_bytes = BytesIO()
    writer = ImageWriter()
    code = barcode.generate('code128', data, writer=writer,output=barcode_bytes)
    return barcode_bytes.getvalue()

def load_random_template_image():
    current_dir = Path(__file__).parent
    templates_dir = current_dir / "templates_images"
    
    image_files = list(templates_dir.glob("*.png"))
    if not image_files:
        return None
    random_image_path = random.choice(image_files)
    return Image.open(random_image_path)

def generate_qrcode_download(data, qr_color=None, background_color=None, style_point=None, image_url=None):
    qr_code_data = generate_qrcode(data, qr_color, background_color, style_point, image_url)
    template_img = load_random_template_image()
    if template_img is None:
        return qr_code_data
    image_stream = BytesIO(qr_code_data)
    template_w, template_h = template_img.size # template_img must be a square
    unit_w = template_w // 8
    new_size_template = (template_w , template_h + (unit_w))
    new_size_qr_code = ((unit_w * 6) , (unit_w * 6)) 

    qr_code_img = Image.open(image_stream) 
    template_img = resizing_image(template_img, target_size=new_size_template)
    qr_code_img = resizing_image(qr_code_img, target_size=new_size_qr_code)
    template_img.paste(qr_code_img,(unit_w, unit_w, unit_w + qr_code_img.size[0], unit_w + qr_code_img.size[1]))
    constant_w = 600
    new_size_final = (constant_w, (new_size_template[1] * constant_w) // new_size_template[0])
    template_img = resizing_image(template_img, target_size=new_size_final, border_size=0)

    img_bytes = BytesIO()
    template_img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()
    

def read_qrcode(image_path_or_bytes):
    try:
        if isinstance(image_path_or_bytes, bytes):
            image = Image.open(BytesIO(image_path_or_bytes))
        else:
            image = Image.open(image_path_or_bytes)
        decoded_objects = decode(image)
        result = []
        if decoded_objects:
            for obj in decoded_objects:
                rect = obj.rect
                left, top, width, height = rect.left, rect.top, rect.width, rect.height
                box = (left, top, left + width, top + height)
                cropped_image = image.crop(box)
                buffered = BytesIO()
                cropped_image.save(buffered, format="PNG")
                base64_image = b64encode(buffered.getvalue()).decode("utf-8")
                
                result.append({
                    "text": obj.data.decode("utf-8"),
                    "image_base64": base64_image
                })
            return result
        else:
            return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))