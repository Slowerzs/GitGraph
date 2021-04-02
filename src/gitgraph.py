from graphviz import Digraph
from git import Repo, InvalidGitRepositoryError, Head, Remote
from typing import List, Set
import sys


class GitGraph:
	def __init__(self, paths):
		self.repos = []
		for path in paths:
			try:
				self.repos.append(Repo(path))
			except InvalidGitRepositoryError:
				print("Un des dossiers proposé n'est pas un dépot git.")
				sys.exit(1)

	def getBranches(self) -> Set[Head]:
	    branches = []
	    for repo in self.repos :
	        branches += repo.branches
	    return set(branches)
	    
	def getRemotes(self, repo: Repo) -> Set[Remote]:
	    remotes = []
	    for repo in self.repos :
	        remotes += repo.remotes
	    return set(remotes)
	    
	def createSubGraphRemote(self, branch: Remote) -> Digraph:
            graph = Digraph()
            repo = branch.repo

            for ref in repo.iter_commits(branch):
                graph.node(ref.hexsha)
                for parent in ref.parents:
                    graph.edge(ref.hexsha, parent.hexsha)	

            return graph

	def createSubGraph(self, branch: Head) -> Digraph:
            graph = Digraph()
            repo = branch.repo

            for ref in repo.iter_commits(branch):
                    graph.node(ref.hexsha)
                    for parent in ref.parents:
                            graph.edge(ref.hexsha, parent.hexsha)	
            
            return graph
