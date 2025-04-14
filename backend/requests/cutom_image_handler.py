from PIL import Image, ImageDraw, ImageFont
import io
from .image_tasking import ImageTasking


class ImageHandler(ImageTasking):
    def edit(self, image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        
        watermark_text = "MIPT"
        # text_width, text_height = draw.textsize(watermark_text, font=font)
        # position = (image.width - text_width - 10, image.height - text_height - 10)

        draw.text((0, 0), watermark_text, fill=(255, 255, 255, 128), font=font)

        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)

        return output.getvalue()
