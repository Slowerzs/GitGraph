import gitgraph
from os import listdir, path
from graphviz import Digraph

if __name__ == '__main__':
    ggraph = gitgraph.GitGraph([path.join("/sources", i) for i in listdir("/sources")])
    ggraph.render()
