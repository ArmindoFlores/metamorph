import heapq
import json
import os
import typing


class GraphNode:
    def __init__(self, extension):
        self.extension = extension
        self.children: typing.List[typing.Tuple["GraphNode", int, str]] = []
        
    def __repr__(self):
        return f"<GraphNode ext={self.extension}>"
    
    def __hash__(self):
        return hash(self.extension)
        
    def add_children(self, children: typing.List[typing.Tuple["GraphNode", int, str]]):
        self.children.extend(children)
        
    def conversion_function_to(self, to: str):
        for child, _, conversion_func in self.children:
            if child.extension != to:
                continue
            return conversion_func
        

def graph_search(start: GraphNode, goal: GraphNode):
    """
    Perform Dijkstra's algorithm to find the shortest conversion path from start to goal.
    """
    priority_queue = [(0, id(start), start, [])]  # (cost, unique_id, current_node, path)
    visited = set()
    
    while priority_queue:
        cost, _, current, path = heapq.heappop(priority_queue)
        
        if current in visited:
            continue
        
        visited.add(current)
        path = path + [current.extension]
        
        if current.extension == goal.extension:
            return path
        
        for neighbor, edge_cost, _ in current.children:
            if neighbor not in visited:
                heapq.heappush(priority_queue, (cost + edge_cost, id(neighbor), neighbor, path))
    
    return None

def init_formats():
    formats_file = os.path.join(os.path.dirname(__file__), "formats.json")
    with open(formats_file, "r") as f:
        formats = json.load(f)
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
    