import argparse
import os
import sys
import tempfile

from conversions import conversions
from formats import find_path
from utils import file_format_heuristic


def main(args: argparse.Namespace):
    input_file_path =  args.input_file    
    output_file_path =  args.output_file
    
    if not os.path.isfile(input_file_path):
        print(f"Couldn't find the input file at '{input_file_path}'")
        return 2
    if os.path.isfile(output_file_path) and not args.overwrite:
        print(f"Output file already exists. Add the --overwrite flag to overwrite")
        return 1
        
    starting_format = file_format_heuristic(input_file_path)
    ending_format = file_format_heuristic(output_file_path, check_contents=False)
    
    if starting_format is None:
        print(f"Couldn't figure out the format for file '{input_file_path}'")
        return 1

    if ending_format is None:
        print(f"Couldn't figure out the format for file '{output_file_path}'")
        return 1
    
    path = find_path(starting_format, ending_format)
    if path is None:
        print(f"No valid conversion path from {starting_format} to {ending_format} was found")
        return 1
        
    print("Valid conversion path found: ", end="")
    for i, (src, dst, _) in enumerate(path):
        if i == 0:
            print(src, end="")
        print(f" -> {dst}", end="")
    print()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        working_file = input_file_path
        basename = os.path.join(tmpdir, os.path.basename(working_file))
        for src, dst, function_name in path:
            new_file = basename + f".{dst}"
            conversions[function_name](working_file, new_file)
            working_file = new_file
        if os.path.isfile(output_file_path):
            os.remove(output_file_path)
        os.rename(working_file, output_file_path)
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A program to convert between most file extensions")
    parser.add_argument("input_file", type=str, help="The input file to be converted")
    parser.add_argument("output_file", type=str, help="The output file path")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Overwrite the output file if it exists")
    args = parser.parse_args()
    sys.exit(main(args))
