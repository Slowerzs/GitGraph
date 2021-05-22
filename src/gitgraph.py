from graphviz import Digraph
from git import Repo, InvalidGitRepositoryError, Head, Remote
from typing import List, Set
import sys


class GitGraph:
    def __init__(self, paths):
        self.repos = []
        self.branches = []
        self.remote = Repo("/remote")

        for path in paths:
            try:
                self.repos.append(Repo(path))
            except InvalidGitRepositoryError:
                print("Un des dossiers proposé n'est pas un dépot git.")
                sys.exit(1)


        self.branches += self.getBranches()

    def render(self, count: int) -> None:
        self.generateFinalGraph(self.branches).render("/output/output_dot_" + str(count))


    def getBranches(self) -> List[Head]:
        branches = []
        for repo in self.repos :
            branches += repo.branches
        return branches

    def createSubGraphRemote(self, prefix: str) -> Digraph:
        graph = Digraph()
        repo = self.remote
        i = 0
        for ref in repo.iter_commits("main"):
            graph.node(prefix + ref.hexsha, label=ref.message)
            if i==0 :
                graph.node(prefix+"remote", label="Remote "+prefix[:-1], color="grey", fontcolor="grey")
                graph.edge(prefix+"remote", prefix + ref.hexsha, color="grey")
            for parent in ref.parents:
                graph.edge(prefix + ref.hexsha, prefix + parent.hexsha)
            i = 1

        return graph

    def createSubGraph(self, branch: Head, prefix: str) -> Digraph:
        graph = Digraph()
        repo = branch.repo
        graph.node(prefix+"local", label="Dépot local "+prefix[:-1], color="grey", fontcolor="grey")
        graph.edge(prefix+"local", prefix + branch.commit.hexsha, color="grey")
        for ref in repo.iter_commits(branch):
            graph.node(prefix + ref.hexsha, label=ref.message)
            for parent in ref.parents:
                graph.edge(prefix + ref.hexsha, prefix + parent.hexsha)

        return graph


    def generateFinalGraph(self, branches: List[Head]) -> Digraph:
        graph = Digraph()
        i = 0
        for branch in branches:
            temp_graph = self.createSubGraph(branch, str(i) + "_")
            graph.subgraph(temp_graph)
            i += 1

        temp_graph = self.createSubGraphRemote(str(i) + "_")
        graph.subgraph(temp_graph)

        return graph
