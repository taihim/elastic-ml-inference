from io import BytesIO
from pathlib import Path

from PIL import Image


def load_img_from_path(file_path: Path) -> Image:
    """Loads an image from a file path."""
    with open(file_path, "rb+") as f:
        img = Image.open(f)
        img.load()
    return img


def load_img(img_bytes: bytes) -> Image:
    """Loads an image from a byte stream."""
    img_buffer = BytesIO(img_bytes)
    img = Image.open(img_buffer)
    img.load()
    return img
