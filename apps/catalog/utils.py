import io
import os

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

MAX_DIMENSION = 1600  # px no lado maior
JPEG_QUALITY = 82


def compress_image(image_field_file, max_dimension=MAX_DIMENSION, quality=JPEG_QUALITY):
    """
    Redimensiona (se necessário) e recomprime a imagem antes de salvar,
    preservando o formato original (png/webp mantêm transparência).
    """
    image_field_file.seek(0)
    img = Image.open(image_field_file)
    original_format = (img.format or "JPEG").upper()

    if img.mode in ("RGBA", "P") and original_format == "JPEG":
        img = img.convert("RGB")

    width, height = img.size
    if max(width, height) > max_dimension:
        ratio = max_dimension / max(width, height)
        img = img.resize((int(width * ratio), int(height * ratio)), Image.LANCZOS)

    buffer = io.BytesIO()
    save_kwargs = {"optimize": True}
    if original_format in ("JPEG", "JPG"):
        save_kwargs["quality"] = quality
        img.save(buffer, format="JPEG", **save_kwargs)
        content_type = "image/jpeg"
    elif original_format == "WEBP":
        save_kwargs["quality"] = quality
        img.save(buffer, format="WEBP", **save_kwargs)
        content_type = "image/webp"
    else:  # PNG e demais
        img.save(buffer, format="PNG", **save_kwargs)
        content_type = "image/png"

    buffer.seek(0)
    name = os.path.basename(image_field_file.name)
    return InMemoryUploadedFile(buffer, None, name, content_type, buffer.getbuffer().nbytes, None)
