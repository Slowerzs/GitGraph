import gitgraph
from os import listdir, path
from graphviz import Digraph
from git import Repo
import shlex
import argparse


class GitGraphDrawer():

    def __init__(self):
        self.currentRepo = None

    def switch(self, gitName: str) -> None:
        self.currentRepo = Repo(path.join("/sources", gitName))

    def render(self) -> None: 
        ggraph = gitgraph.GitGraph([path.join("/sources", i) for i in listdir("/sources")])
        ggraph.render()

    def commmit(self, commitMessage: str) -> None:
        self.currentRepo.git.commit(m=commitMessage)

    def add(self, path: str) -> None:
        self.currentRepo.git.add(path)

if __name__ == '__main__':
    

    graphDrawer = GitGraphDrawer()

    with open("/commands.txt", "r") as f:
        commands = f.readlines()

    assert commands[0].startswith("switch"), "The first command should be a switch statement"

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='subcommand')

    parser_commit = subparser.add_parser('commit')
    parser_commit.add_argument("-m")

    parser_commit = subparser.add_parser('switch')
    parser_commit.add_argument("branch_name")

    parser_commit = subparser.add_parser('add')
    parser_commit.add_argument("path")
    
    parser_commit = subparser.add_parser('render')
    
    for command in commands:
        args = parser.parse_args(shlex.split(command))
        
        if args.subcommand == "switch":
            graphDrawer.switch(args.branch_name)
        if args.subcommand == "render":
            graphDrawer.render()
        if args.subcommand == "commit":
            graphDrawer.commit(args.m)
        if args.subcommand == "add":
            graphDrawer.add(args.path)



