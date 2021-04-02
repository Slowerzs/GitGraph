import gitgraph

if __name__ == '__main__':
	ggraph = gitgraph.GitGraph(["/home/slowerzs/CassiopeeGitMOOC"])
	b = ggraph.getBranches()
	for br in b:
		ggraph.createSubGraph(br)	

