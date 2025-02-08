__all__ = [
    "conversions"
]

import os

from PIL import Image


def rename(src: str, dst: str):
    os.rename(src, dst)
    
def img_to_img(src: str, dst: str):
    # TODO: it would be cool to parse PIL.features.pilinfo()
    # TODO: to figure out what extensions we can use
    img = Image.open(src)
    if dst.endswith(("jpg", "jpeg", "bmp")):
        img = img.convert("RGB")
    img.save(dst)

conversions = {
    "rename": rename,
    "img_to_img": img_to_img
}
