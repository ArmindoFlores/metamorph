import json
import os

import PIL
import PIL.Image

from utils import GraphNode, graph_search


def get_PIL_formats():
    """This function uses PIL to determine all possible trivial image conversions"""
    format_to_extension = {}
    for extension, format_ in PIL.Image.registered_extensions().items():
        format_to_extension.setdefault(format_, []).append(extension[1:])
        
    possible_paths = {}
    for format_ in PIL.Image.OPEN:
        if format_ not in format_to_extension:
            continue
        extensions = format_to_extension[format_]
        for extension in extensions:
            possible_paths[extension] = {}
            for other_format in PIL.Image.SAVE:
                if other_format not in format_to_extension:
                    continue
                for other_extension in format_to_extension[other_format]:
                    possible_paths[extension][other_extension] = { "cost": 2, "function": "img_to_img" }
    return possible_paths

def init_formats():
    formats_file = os.path.join(os.path.dirname(__file__), "formats.json")
    with open(formats_file, "r") as f:
        formats = json.load(f)
    PIL_formats = get_PIL_formats()
    formats.update(PIL_formats)
    return formats

def build_graph(formats):
    nodes = {}
    for format_name in formats.keys():
        nodes[format_name] = GraphNode(format_name)
    for format_name, format_conversions in formats.items():
        nodes[format_name].add_children(
            [
                (nodes.get(conversion_ext, GraphNode(conversion_ext)), details["cost"], details["function"])
                for conversion_ext, details in format_conversions.items()
            ]
        )
    return nodes

def find_path(in_format: str, out_format: str):
    graph = build_graph(init_formats())
    if in_format not in graph:
        print(f"Error: Invalid starting format '{in_format}'")
        return None
    
    # FIXME: we're missing a step where we check the library requirements
    # for converting; for example, we might need libwebp, ffmpeg, etc...
    # If we find a viable path but not one that meets library requirements,
    # we can suggest which libraries to install to the user.
    
    starting_node = graph[in_format]
    ending_node = graph.get(out_format, GraphNode(out_format))
    path = graph_search(starting_node, ending_node)
    if path is None:
        return None
    
    blueprint_conversion = [
        (src, dst, graph[src].conversion_function_to(dst)) for src, dst in zip(path[:-1], path[1:])
    ]
    return blueprint_conversion
    