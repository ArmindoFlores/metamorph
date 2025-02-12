__all__ = [
    "find_path",
    "init_formats",
    "build_graph"
]

import json
import os
import typing

import PIL
import PIL.Image
import pypandoc

from mm.utils import GraphNode, GraphNodeEdge, graph_search


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

def get_pdf2image_formats():
    """This function uses PIL to determine all possible conversions from pdf to an image"""
    # FIXME: this only works with poppler installed
    format_to_extension = {}
    for extension, format_ in PIL.Image.registered_extensions().items():
        format_to_extension.setdefault(format_, []).append(extension[1:])
    
    possible_paths = {
        "pdf": {}
    }
    for format_ in PIL.Image.SAVE:
        if format_ not in format_to_extension:
            continue
        extensions = format_to_extension[format_]
        for extension in extensions:
            possible_paths["pdf"][extension] = {
                "cost": 10,
                "function": "pdf2img",
                "dependencies": ["poppler"]
            }
    return possible_paths

def normalize_pandoc_format(fmt):
    formats = {
        "biblatex": "bib",
        "bibtex": "bib",
        "bits": "xml",
        "commonmark": "md",
        "commonmark_x": "md",
        "creole": "creole",
        "csljson": "json",
        "csv": "csv",
        "djot": "dj",
        "docbook": "xml",
        "docx": "docx",
        "dokuwiki": "txt",
        "endnotexml": "xml",
        "epub": "epub",
        "fb2": "fb2",
        "gfm": "md",
        "haddock": "hs",
        "html": "html",
        "ipynb": "ipynb",
        "jats": "xml",
        "jira": "txt",
        "json": "json",
        "latex": "tex",
        "man": "man",
        "markdown": "md",
        "markdown_github": "md",
        "markdown_mmd": "md",
        "markdown_phpextra": "md",
        "markdown_strict": "md",
        "mdoc": "mdoc",
        "mediawiki": "wiki",
        "muse": "muse",
        "native": "txt",
        "odt": "odt",
        "opml": "opml",
        "org": "org",
        "ris": "ris",
        "rst": "rst",
        "rtf": "rtf",
        "t2t": "txt",
        "textile": "textile",
        "tikiwiki": "txt",
        "tsv": "tsv",
        "twiki": "txt",
        "typst": "typ",
        "vimwiki": "wiki",
    }

    fmt = formats.get(fmt, fmt)
    # rst format can have extensions
    if fmt[:3] == "rst":
        fmt = "rest" + fmt[3:]
    return fmt

def get_pandoc_formats():
    """This function uses pandoc to determine all possible trivial document conversions"""
    from_formats, to_formats = pypandoc.get_pandoc_formats()
    from_extensions = [normalize_pandoc_format(from_format) for from_format in from_formats]
    to_extensions = [normalize_pandoc_format(to_format) for to_format in to_formats]
    possible_paths = {}
    for from_extension in from_extensions:
        possible_paths[from_extension] = {
            to_extension: { "cost": 5, "function": "pandoc_convert" }
            for to_extension in to_extensions
        }
    return possible_paths

def init_formats():
    formats_file = os.path.join(os.path.dirname(__file__), "formats.json")
    with open(formats_file, "r") as f:
        formats = json.load(f)
    # FIXME: use a deep update (merge inner dictionaries)
    PIL_formats = get_PIL_formats()
    pandoc_formats = get_pandoc_formats()
    pdf2latex_formats = get_pdf2image_formats()
    formats.update(PIL_formats)
    formats.update(pandoc_formats)
    formats.update(pdf2latex_formats)
    return formats

def build_graph(formats):
    nodes = {}
    for format_name in formats.keys():
        nodes[format_name] = GraphNode(format_name)
    for format_name, format_conversions in formats.items():
        nodes[format_name].add_children(
            [
                GraphNodeEdge(
                    child=nodes.get(conversion_ext, GraphNode(conversion_ext)),
                    cost=details["cost"],
                    conversion_function=details["function"],
                    dependencies=details.get("dependencies", [])
                )
                for conversion_ext, details in format_conversions.items()
            ]
        )
    return nodes

def find_path(graph: dict, dependencies: typing.Set[str], in_format: str, out_format: str, ignore_dependencies: bool = False):
    if in_format not in graph:
        print(f"Error: Invalid starting format '{in_format}'")
        return None, None
    
    # FIXME: we're missing a step where we check the library requirements
    # for converting; for example, we might need libwebp, ffmpeg, etc...
    # If we find a viable path but not one that meets library requirements,
    # we can suggest which libraries to install to the user.
    
    starting_node = graph[in_format]
    ending_node = graph.get(out_format, GraphNode(out_format))
    path, requirements = graph_search(starting_node, ending_node, dependencies, ignore_dependencies)
    if path is None or requirements is None:
        return None, None
    
    blueprint_conversion = [
        (src, dst, graph[src].conversion_function_to(dst)) for src, dst in zip(path[:-1], path[1:])
    ]

    return blueprint_conversion, requirements
    