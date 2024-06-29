from pathlib import Path

from PIL.Image import Image

from src.utils import load_img_from_bytes, load_img_from_path


# TODO: remove test images from the repo and download them from the internet instead
def test_load_img_from_path() -> None:
    """Test load_img_from_path function."""
    img_path = Path("./tests/data/bird.JPEG")
    img = load_img_from_path(img_path)
    assert isinstance(img, Image)


def test_load_img_from_bytes() -> None:
    """Test load_img_from_bytes function."""
    img_path = Path("./tests/data/bird.JPEG")
    with open(img_path, "rb") as f:
        img_bytes = f.read()
    img = load_img_from_bytes(img_bytes)
    assert isinstance(img, Image)
