__all__ = [
    "file_format_heuristic"
]

import os

def file_format_heuristic(filepath: str, check_contents: bool = True):
    basename = os.path.basename(filepath)
    splitname = basename.split(".")
    extension = splitname[-1] if len(splitname) > 1 else None
    
