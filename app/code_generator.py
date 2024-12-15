from io import BytesIO
from PIL import Image, ImageOps, ImageColor
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *
from barcode.writer import ImageWriter
import qrcode,barcode,requests

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



def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_qrcode(data, qr_color=None, background_color=None, style_point=None, image_url=None):

    qr_color = '#000000' if qr_color is None else '#000000' if qr_color=='' else qr_color 
    background_color = '#ffffff' if background_color is None else '#ffffff' if background_color=='' else background_color
    style_point = 'square' if style_point is None else 'square' if style_point=='' else style_point

    valid_style_points = ['square', 'gapped_square', 'circle', 'rounded', 'vertical_bar', 'horizontal_bar']
    if style_point not in valid_style_points:
        raise HTTPException(status_code=400, detail="Invalid style_point")

    logo = None
    if image_url and image_url!='':
        logo = process_resize_image(image_url,border_color=background_color)
        logo = logo.resize((50, int((50 / float(logo.size[0])) * float(logo.size[1]))), Image.LANCZOS)
        logo = logo.convert('RGBA')
        background = Image.new('RGBA', logo.size, hex_to_rgb(background_color) + (255,))
        background.paste(logo, (0, 0), logo)
        logo = background
        
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

def generate_barcode(data):
    # Create a Code128 barcode
    barcode_bytes = BytesIO()
    writer = ImageWriter()
    code = barcode.generate('code128', data, writer=writer,output=barcode_bytes)
    return barcode_bytes.getvalue()