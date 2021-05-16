import gitgraph
from os import listdir, path, urandom
from graphviz import Digraph
from git import Repo
import shlex
import argparse


class GitGraphDrawer():

    def __init__(self):
        self.currentRepo = None

    def switch(self, gitName: str) -> None:
        self.currentRepo = Repo(path.join("/sources", gitName))
        self.currentRepo.config_writer().set_value("user", "name", "myusername").release()
        self.currentRepo.config_writer().set_value("user", "email", "myemail@localhost").release()

    def render(self) -> None: 
        ggraph = gitgraph.GitGraph([path.join("/sources", i) for i in listdir("/sources")])
        ggraph.render()

    def commit(self, commitMessage: str) -> None:
        self.currentRepo.git.commit(m=commitMessage)

    def add(self, pathToAdd: str) -> None:
        fullPath = path.join(self.currentRepo.working_dir, pathToAdd)
        if path.isfile(fullPath):
            #Modifications are needed for add to work, so we add random content
            with open(fullPath, "a") as f:
                f.write(urandom(50).hex())
            self.currentRepo.git.add(pathToAdd)
        elif path.isdir(fullPath):
            #Modifications are needed for add to work, so we add a new file
            open(path.join(fullPath, urandom(50).hex()), "w").close()
            self.currentRepo.git.add(pathToAdd)
        else:
            #Modifications are needed for add to work, so we create a new file
            open(fullPath, "w").close()
            self.currentRepo.git.add(pathToAdd)

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



