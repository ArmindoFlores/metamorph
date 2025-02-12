__all__ = [
    "file_format_heuristic"
]

import heapq
import os
import typing
from dataclasses import dataclass

import filetype


class GraphNode:
    def __init__(self, extension):
        self.extension = extension
        self.edges: typing.List[GraphNodeEdge] = []
        
    def __repr__(self):
        return f"<GraphNode ext={self.extension}>"
    
    def __hash__(self):
        return hash(self.extension)
        
    def add_children(self, edge: typing.List["GraphNodeEdge"]):
        self.edges.extend(edge)
        
    def conversion_function_to(self, to: str):
        for edge in self.edges:
            if edge.child.extension != to:
                continue
            return edge.conversion_function
        
@dataclass
class GraphNodeEdge:
    child: GraphNode
    cost: int
    conversion_function: str
    dependencies: typing.List[str]


def graph_search(start: GraphNode, goal: GraphNode):
    """
    Perform Dijkstra's algorithm to find the shortest conversion path from start to goal.
    """
    priority_queue: typing.List[typing.Tuple[int, int, GraphNode, typing.List[str]]]  = [(0, id(start), start, [])]  # (cost, unique_id, current_node, path)
    visited = set()
    
    while priority_queue:
        cost, _, current, path = heapq.heappop(priority_queue)
        
        if current in visited:
            continue
        
        visited.add(current)
        path = path + [current.extension]
        
        if current.extension == goal.extension:
            return path
        
        for edge in current.edges:
            if edge.child not in visited:
                heapq.heappush(priority_queue, (cost + edge.cost, id(edge.child), edge.child, path))
    
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
