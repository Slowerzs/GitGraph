from graphviz import Digraph
from git import Repo, InvalidGitRepositoryError, Head, Remote
from typing import List, Set
import sys


class GitGraph:
    def __init__(self, paths):
        self.repos = []
        self.branches = []
        self.remotes = []
            
        for path in paths:
            try:
                self.repos.append(Repo(path))
            except InvalidGitRepositoryError:
                print("Un des dossiers proposé n'est pas un dépot git.")
                sys.exit(1)
        
        self.branches += self.getBranches()
        self.remotes += self.getRemotes()
        

    def render(self) -> None:
        self.generateFinalGraph(self.branches, self.remotes).render("/output/output_dot")


    def getBranches(self) -> List[Head]:
        branches = []
        for repo in self.repos :
            branches += repo.branches
        return branches
        
    def getRemotes(self) -> List[Remote]:
        remotes = []
        for repo in self.repos :
            remotes += repo.remotes
        return list(set(remotes))
        
    def createSubGraphRemote(self, branch: Remote, prefix: str) -> Digraph:
        graph = Digraph()
        repo = branch.repo

        for ref in repo.iter_commits(branch):
            graph.node(prefix + ref.hexsha, label=ref.message)
            for parent in ref.parents:
                graph.edge(prefix + ref.hexsha, prefix + parent.hexsha)	

        return graph

    def createSubGraph(self, branch: Head, prefix: str) -> Digraph:
        graph = Digraph()
        repo = branch.repo
        for ref in repo.iter_commits(branch):
                graph.node(prefix + ref.hexsha, label=ref.message)
                for parent in ref.parents:
                        graph.edge(prefix + ref.hexsha, prefix + parent.hexsha)	
        
        return graph


    def generateFinalGraph(self, branches: List[Head], remotes: List[Remote]) -> Digraph:
        graph = Digraph()
        i = 0
        for branch in branches:
            temp_graph = self.createSubGraph(branch, str(i) + "_")
            graph.subgraph(temp_graph)
            i += 1

        for remote in remotes:
            temp_graph = self.createSubGraphRemote(remote, str(i) + "_")
            graph.subgraph(temp_graph)
            i += 1

        return graph


