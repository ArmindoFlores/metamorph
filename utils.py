__all__ = [
    "file_format_heuristic"
]

import os

import filetype

def file_format_heuristic(filepath: str, check_contents: bool = True):
    basename = os.path.basename(filepath)
    splitname = basename.split(".")
    extension = splitname[-1] if len(splitname) > 1 else None
    content_format_guess = None
    
    if check_contents:
        try:
            with open(filepath, "rb") as f:
                file_header = f.read(2048)
                guess = filetype.guess(file_header)
                if guess is not None:
                    content_format_guess = guess.EXTENSION
        except Exception:
            pass
        
    if extension is None:
        return content_format_guess
    if content_format_guess is None:
        return extension
      
    if content_format_guess != extension:
        print(f"Warning: file extension is {extension} but detected contents of a {content_format_guess} file")  
    return extension
