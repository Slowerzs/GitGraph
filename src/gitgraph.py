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

    def render(self, count: int, startBranch: Head, endBranch: Head, failed: bool) -> None:
        self.generateFinalGraph(self.branches, startBranch, endBranch, failed).render("/output/output_dot_" + str(count))


    def getBranches(self) -> List[Head]:
        branches = []
        for repo in self.repos :
            branches += repo.branches
        return branches

    def createSubGraphRemote(self, branch: Head, prefix: str) -> Digraph:

        repo = self.remote
        graph = Digraph(name="cluster" + prefix.split("_")[0])
        graph.node(prefix+"remote", label="Dépot distant", color="grey", fontcolor="grey")
        graph.edge(prefix+"remote", prefix + branch.commit.hexsha, color="grey")
        for ref in repo.iter_commits(branch.name):
            graph.node(prefix + ref.hexsha, label=ref.message.strip())
            for parent in ref.parents:
                graph.edge(prefix + ref.hexsha, prefix + parent.hexsha)

        return graph

    def createSubGraph(self, branch: Head, prefix: str) -> Digraph:
        graph = Digraph(name="cluster" + prefix.split("_")[0])
        repo = branch.repo
        graph.node(prefix+"local", label="Dépot local " + prefix[:-1], color="grey", fontcolor="grey")
        graph.edge(prefix+"local", prefix + branch.commit.hexsha, color="grey")
        for ref in repo.iter_commits(branch):
            graph.node(prefix + ref.hexsha, label=ref.message.strip())
            for parent in ref.parents:
                graph.edge(prefix + ref.hexsha, prefix + parent.hexsha)

        return graph


    def generateFinalGraph(self, branches: List[Head], startBranch: Head, endBranch: Head, failed: bool) -> Digraph:
        graph = Digraph()
        graph.attr(compound='true')
        i = 0

        colors = { False: "blue", True: "red" }

        savedStart = None
        savedEnd = None

        for branch in branches:
            prefix = str(i) + "_"
            temp_graph = self.createSubGraph(branch, prefix)
            if branch == startBranch and branch.repo == startBranch.repo:
                savedStart = prefix + branch.commit.hexsha
            graph.subgraph(temp_graph)
            i += 1

        for branch in self.remote.branches:
            prefix = str(i) + "_"
            temp_graph = self.createSubGraphRemote(branch, prefix)
            graph.subgraph(temp_graph)
            if branch == endBranch:
                savedEnd = prefix + branch.commit.hexsha
            i += 1
	
        if savedStart != None and savedEnd != None:
            graph.edge(savedStart, savedEnd, color=colors[failed], constraint="false")

        return graph



