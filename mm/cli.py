import argparse
import os
import shutil
import sys
import tempfile

from mm.conversions import conversions
from mm.formats import build_graph, init_formats, find_path
from mm.utils import file_format_heuristic
from mm.dependencies import available_dependencies


def convert(args: argparse.Namespace):
    deps = available_dependencies(args)

    input_file_path = args.input_file
    output_file_path = args.output_file
    
    if not os.path.isfile(input_file_path):
        print(f"Couldn't find the input file at '{input_file_path}'")
        return 2
    if os.path.isfile(output_file_path) and not args.overwrite:
        print(f"Output file already exists. Add the --overwrite flag to overwrite")
        return 1
        
    starting_format = file_format_heuristic(input_file_path) if args.input_format is None else args.input_format
    ending_format = file_format_heuristic(output_file_path, check_contents=False) if args.output_format is None else args.output_format
    
    if starting_format is None:
        print(f"Couldn't figure out the format for file '{input_file_path}'")
        return 1

    if ending_format is None:
        print(f"Couldn't figure out the format for file '{output_file_path}'")
        return 1
    
    formats = init_formats()
    graph = build_graph(formats)
    path, requirements = find_path(graph, deps, starting_format, ending_format, args.ignore_dependencies)
    if path is None or requirements is None:
        print(f"No valid conversion path from {starting_format} to {ending_format} was found")
        return 1
    
    if not args.ignore_dependencies and not deps.issuperset(requirements):
        missing = requirements.difference(deps)
        print(f"Warning: missing required tools ({', '.join(missing)})", end="")
        if not args.dry_run:
            yn = input(f"; proceed with coversion? (y/n) ")
            if yn != "y":
                return 0
        else:
            print()
        
    print("Valid conversion path found: ", end="")
    for i, (src, dst, _) in enumerate(path):
        if i == 0:
            print(src, end="")
        print(f" -> {dst}", end="")
    print()
    print(f"Required tools: {requirements}")

    if args.dry_run:
        return 0
    
    with tempfile.TemporaryDirectory() as tmpdir:
        working_file = input_file_path
        basename = os.path.join(tmpdir, os.path.basename(working_file))
        for src, dst, function_name in path:
            new_file = basename + f".{dst}"
            conversions[function_name](working_file, new_file)
            working_file = new_file
        if os.path.isfile(output_file_path):
            os.remove(output_file_path)
        shutil.move(working_file, output_file_path)
    
    return 0

def main():
    parser = argparse.ArgumentParser("mm", description="A program to convert between most file extensions")
    parser.add_argument("input_file", type=str, help="The input file to be converted")
    parser.add_argument("output_file", type=str, help="The output file path")
    parser.add_argument("--overwrite", "-o", action="store_true", help="Overwrite the output file if it exists")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Don't do the conversion, only output the path")
    parser.add_argument("--ignore-dependencies", "-i", action="store_true", help="Ignore missing dependencies")
    parser.add_argument("--input-format", type=str, help="Specify the input format")
    parser.add_argument("--output-format", type=str, help="Specify the output format")
    
    parser.add_argument("--ffmpeg-path", type=str, help="Path to the ffmpeg binary")
    parser.add_argument("--poppler-path", type=str, help="Path to the pdftotext binary")
    
    args = parser.parse_args()
    sys.exit(convert(args))
