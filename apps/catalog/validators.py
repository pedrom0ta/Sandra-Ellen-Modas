import os

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_image_file(file):
    """Valida extensão, MIME type (via Pillow, não só o header do navegador) e tamanho."""
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f"Extensão '{ext}' não permitida. Use: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}."
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(f"Arquivo maior que {settings.MAX_UPLOAD_SIZE_MB}MB.")

    # Verifica o conteúdo real do arquivo (não confia só na extensão)
    try:
        from PIL import Image
        file.seek(0)
        img = Image.open(file)
        img.verify()
        real_mime = Image.MIME.get(img.format)
        file.seek(0)
    except Exception:
        raise ValidationError("Arquivo de imagem inválido ou corrompido.")

    if real_mime not in settings.ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError(f"Tipo de imagem '{real_mime}' não permitido.")
