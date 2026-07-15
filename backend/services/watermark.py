import os
from datetime import datetime
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


PROCESSED_FOLDER = "processed"

os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def add_watermark(image_path: str, document_id: int):

    image = Image.open(image_path)

    image = image.convert("RGBA")

    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))

    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()

    text = f"""PROCESSED

Invoice ID : {document_id}

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    draw.multiline_text(
        (30, 30),
        text,
        fill=(255, 0, 0, 180),
        font=font,
        spacing=6
    )

    watermarked = Image.alpha_composite(image, overlay)

    filename = os.path.basename(image_path)

    output_path = os.path.join(
        PROCESSED_FOLDER,
        filename
    )

    watermarked.convert("RGB").save(output_path)

    return output_path