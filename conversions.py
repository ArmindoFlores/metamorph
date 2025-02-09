__all__ = [
    "conversions"
]

import os

from PIL import Image


def rename(src: str, dst: str):
    os.rename(src, dst)
    
def img_to_img(src: str, dst: str):
    img = Image.open(src)
    if src.endswith((".png", ".webp", ".ico")) and not dst.endswith((".png", ".webp", ".ico")):
        img = img.convert("RGB")
    img.save(dst)

conversions = {
    "rename": rename,
    "img_to_img": img_to_img
}
