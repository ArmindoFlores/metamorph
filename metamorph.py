import argparse
import os
import sys

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
    
    print(f"Going  from {starting_format} to {ending_format}")
        
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A program to convert between most file extensions")
    parser.add_argument("input_file", type=str, help="The input file to be converted")
    parser.add_argument("output_file", type=str, help="The output file path")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Overwrite the output file if it exists")
    args = parser.parse_args()
    sys.exit(main(args))
