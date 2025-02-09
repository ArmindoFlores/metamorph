__all__ = [
    "conversions"
]

import os

from PIL import Image
import pypandoc


def rename(src: str, dst: str):
    os.rename(src, dst)
    
def img_to_img(src: str, dst: str):
    img = Image.open(src)
    if src.endswith((".png", ".webp", ".ico")) and not dst.endswith((".png", ".webp", ".ico")):
        img = img.convert("RGB")
    img.save(dst)
    
def pandoc_covert(src: str, dst: str):
    # FIXME: pandoc's "to" argument excepts a format and not an extension
    ext = dst.split(".")[-1]
    pypandoc.convert_file(src, pypandoc.normalize_format(ext), outputfile=dst)

conversions = {
    "rename": rename,
    "img_to_img": img_to_img,
    "pandoc_convert": pandoc_covert
}
