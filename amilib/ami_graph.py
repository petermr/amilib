"""
for drawing networks/graphs
"""
class AmiGraph:
    """
    grahs can be nested?
    """

    def __init__(self):
        self.subgraphs = []

    def create_subgraph(self):
        subgraph = AmiGraph()
        self.subgraphs.append(subgraph)