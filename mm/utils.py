__all__ = [
    "file_format_heuristic"
]

import heapq
import os
import typing

import filetype


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
