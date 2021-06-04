from graphviz import Digraph
from git import Repo, InvalidGitRepositoryError, Head, Remote
from typing import List, Set
import sys


class GitGraph:
    def __init__(self, paths):
        """Initiates a GitGraph Object

        paths -- a list of path to be added as local repos
        """
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
        """Renders the current state of the all the branches (local and remote)
        
        count -- the number added to the generated file name
        startBranch -- if we have to draw an Arrow, the starting point
        endBranch -- the ending point of the arrow
        failed -- If we draw an error, is it red or blue
        """
        self.generateFinalGraph(self.branches, startBranch, endBranch, failed).render("/output/output_dot_" + str(count))


    def getBranches(self) -> List[Head]:
        """Returns a list of all local branches for all local repos"""
        branches = []
        for repo in self.repos :
            branches += repo.branches
        return branches

    def createSubGraphRemote(self, branch: Head, prefix: str) -> Digraph:
        """Returns a Digraph for a given branch of a remote
        
        branch -- the branch we are creating a graph for
        prefix -- the prefix added to differentiate in the dot commits with the same hash
        """
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
        """Returns a Digraph for a given branch of a local repo
       
        branch -- the branch we are creating a graph for
        prefix -- the prefix added to differentiate in the dot commits with the same hash
        """
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
        """Return a Digraph representing all states of all branches

        branches -- a list of all branches to represent
        startBranch -- if we have to draw an arrow, the starting point
        endBranch -- if we have to draw an arrow, the ending point
        failed -- if we have to draw an arrow, the color
        """
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



