__all__ = [
    "conversions",
]

import argparse
import os
import subprocess

from PIL import Image
import pdf2image
import pypandoc


def rename(src: str, dst: str, args: argparse.Namespace):
    os.rename(src, dst)
    
def img_to_img(src: str, dst: str, args: argparse.Namespace):
    img = Image.open(src)
    if src.endswith((".png", ".webp", ".ico")) and not dst.endswith((".png", ".webp", ".ico")):
        img = img.convert("RGB")
    img.save(dst)
    
def pandoc_covert(src: str, dst: str, args: argparse.Namespace):
    # FIXME: pandoc's "to" argument excepts a format and not an extension
    ext = dst.split(".")[-1]
    pypandoc.convert_file(src, pypandoc.normalize_format(ext), outputfile=dst)
    
def pdf_to_img(src: str, dst: str, args: argparse.Namespace):
    # FIXME: this works better with multiple output files
    images = pdf2image.convert_from_path(src, single_file=True)
    if len(images) == 0:
        print("Error: couldn't convert pdf to image")
        return
    images[0].save(dst)

def ffmpeg_simple(src: str, dst: str, args: argparse.Namespace):
    subprocess.run([args.ffmpeg_path, "-i", src, "-codec", "copy", dst])

conversions = {
    "rename": rename,
    "img_to_img": img_to_img,
    "pandoc_convert": pandoc_covert,
    "pdf2img": pdf_to_img,
    "ffmpeg_simple": ffmpeg_simple,
}
