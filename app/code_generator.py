from io import BytesIO
from PIL import Image, ImageOps, ImageColor
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import *
from qrcode.image.styles.colormasks import *
from barcode.writer import ImageWriter
from pathlib import Path
import qrcode,barcode,requests,random


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def resizing_image(img, target_size=(300, 300), border_size=2, border_color="white"):
    original_width, original_height = img.size
    # Calculate the aspect ratio
    aspect_ratio = original_width / original_height
    # Calculate the target dimensions with cover approach
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

    valid_style_points = ['square', 'gapped_square', 'circle', 'rounded', 'vertical_bar', 'horizontal_bar']
    if style_point not in valid_style_points:
        raise HTTPException(status_code=400, detail="Invalid style_point")

    logo = None
    if image_url and image_url!='':
        image_response = requests.get(image_url)
        original_image = Image.open(BytesIO(image_response.content))
        logo = resizing_image(original_image, target_size=(50,50))
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
    qr_code_img = Image.open(image_stream) 
    qr_code_img = resizing_image(qr_code_img, target_size=(700,700))
    template_img.paste(qr_code_img,(150, 100, 150 + qr_code_img.size[0], 100 + qr_code_img.size[1]))
    template_img = resizing_image(template_img, border_size=0)
    img_bytes = BytesIO()
    template_img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()
    