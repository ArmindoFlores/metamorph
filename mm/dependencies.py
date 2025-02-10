__all__ = [
    "available_dependencies"
]

import argparse
import subprocess
import shutil
import typing


def verify_cmd_utility(filepath: str, flags: typing.List[str], starting_text: str|None):
    if shutil.which(filepath) is None:
        return False
    
    if starting_text is None:
        return True

    try:
        output = subprocess.check_output([filepath, *flags], stderr=subprocess.DEVNULL)
        first_line = output.splitlines()[0].decode(errors="ignore")
        return first_line.startswith(starting_text)
    except (FileNotFoundError, subprocess.CalledProcessError, IndexError):
        return False

def verify_ffmpeg(args: argparse.Namespace) -> bool:
    return verify_cmd_utility(
        args.ffmpeg_path if args.ffmpeg_path else "ffmpeg",
        ["-version"],
        "ffmpeg version"
    )

def verify_poppler(args: argparse.Namespace) -> bool:
    return verify_cmd_utility(
        args.poppler_path if args.poppler_path else "pdftotext",
        [],
        None
    )


def available_dependencies(args: argparse.Namespace):
    deps = (
        ("ffmpeg", verify_ffmpeg),
        ("poppler", verify_poppler),
    )
    return tuple(name for name, verifier in deps if verifier(args))
