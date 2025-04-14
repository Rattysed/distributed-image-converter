from PIL import Image
import io
from .image_tasking import ImageTasking


class ImageHandler(ImageTasking):
    def edit(self, image_bytes):
        main = Image.open(io.BytesIO(image_bytes)).convert('RGBA')
        mark = Image.open('./requests/image_handler/logo.png').convert('RGBA')
        mark = mark.rotate(30, expand=1)

        mask = mark.split()[3].point(lambda x: x // 2)
        mark.putalpha(mask)

        mark_width, mark_height = mark.size
        main_width, main_height = main.size
        aspect_ratio = mark_width / mark_height
        new_mark_width = main_width * 0.4
        mark.thumbnail((int(new_mark_width), int(new_mark_width / aspect_ratio)), Image.LANCZOS)

        tmp_img = Image.new('RGBA', main.size, (255, 255, 255, 0))
        for i in range(0, tmp_img.size[0], mark.size[0]):
            for j in range(0, tmp_img.size[1], mark.size[1]):
                tmp_img.paste(mark, (i, j), mark)

        combined = Image.alpha_composite(main, tmp_img)

        combined = combined.convert('RGB')
        output = io.BytesIO()
        combined.save(output, 'JPEG', quality=100)
        output.seek(0)

        return output.getvalue()
