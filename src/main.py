import gitgraph
from os import listdir, path
from graphviz import Digraph

if __name__ == '__main__':
    ggraph = gitgraph.GitGraph([path.join("/sources", i) for i in listdir("/sources")])
    b = ggraph.getBranches()
    final_graph = Digraph()
    for br in b:
        temp_graph = ggraph.createSubGraph(br)
        final_graph.subgraph(temp_graph)

    final_graph.render("/output/output_dot")
