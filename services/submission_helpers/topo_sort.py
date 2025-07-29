from collections import deque
import queue
from  typing import List
from services.submission_helpers.graph_builder import GraphSchema
from utils.logger import get_logger

logger = get_logger("validation_logger")

def topological_sort(graph: GraphSchema) -> List[str]:
    """
    Perform topological sort on the given graph.
    """
    logger.info("Performing topological sort on the graph...")

    in_degree = {table: 0 for table in graph}

    # Count in-degrees (number of parents)
    for table, node in graph.items():
        for child_relation in node.children:
            if child_relation.table in in_degree:
                in_degree[child_relation.table] += 1

    queue = deque([table for table, degree in in_degree.items() if degree == 0])
    sorted_tables = []

    while queue:
        table = queue.popleft()
        sorted_tables.append(table)

        for child_relation in graph[table].children:
            child = child_relation.table
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(sorted_tables) != len(graph):
        raise ValueError("Graph contains a cycle")
    
    return sorted_tables