import gitgraph
import sys
from string import Template
from os import listdir, path, urandom
from graphviz import Digraph
from git import Repo
import shlex
import argparse
from shutil import copytree
from git import Repo, InvalidGitRepositoryError

class GitGraphDrawer():

    def __init__(self):
        self.currentRepo = None
        self.count = 1

        copytree("/sources", "/locals")

        Repo.init("/remote", bare=True)

        try:
            for repo in [Repo(path.join("/locals", i)) for i in listdir("/locals")]:
                repo.create_remote("custom_remote", "/remote/")
        except InvalidGitRepositoryError:
            print("Un des dossiers proposé n'est pas un dépot git.")
            sys.exit(1)

        repo1 = Repo("/locals/git1")
        repo1.git.push("custom_remote", "main")

    def push(self) -> None:
        self.currentRepo.git.push("custom_remote", "main")

    def switch(self, gitName: str) -> None:
        self.currentRepo = Repo(path.join("/locals", gitName))
        self.currentRepo.config_writer().set_value("user", "name", "myusername").release()
        self.currentRepo.config_writer().set_value("user", "email", "myemail@localhost").release()

    def render(self) -> None:
        ggraph = gitgraph.GitGraph([path.join("/locals", i) for i in listdir("/locals")])
        ggraph.render(self.count)
        self.count += 1

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

    def generateHtml(self) -> None:
        files_data = []
    
        for filename in listdir("/output"):
            if filename.endswith(".pdf"):
                continue

            with open(path.join("/output", filename), 'r') as f:
                file_data = f.read()
                files_data.append('`' + file_data.replace('`', '\\`') + '`')

        data = ','.join(map(str, files_data))

        with open("template.html", "r") as f:
            template_str = f.read()

        template = Template(template_str)
        output = template.substitute({"data": data})

        with open("/output/output.html", "w") as f:
            f.write(output)


if __name__ == '__main__':


    graphDrawer = GitGraphDrawer()

    with open("/commands.txt", "r") as f:
        commands = f.readlines()

    assert commands[0].startswith("switch"), "The first command should be a switch statement"

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='subcommand')

    parser_push = subparser.add_parser('push')

    parser_commit = subparser.add_parser('commit')
    parser_commit.add_argument("-m")

    parser_commit = subparser.add_parser('switch')
    parser_commit.add_argument("branch_name")

    parser_commit = subparser.add_parser('add')
    parser_commit.add_argument("path")

    parser_commit = subparser.add_parser('render')

    for command in commands:
        args = parser.parse_args(shlex.split(command))

        if args.subcommand == "push":
            graphDrawer.push()
        if args.subcommand == "switch":
            graphDrawer.switch(args.branch_name)
        if args.subcommand == "render":
            graphDrawer.render()
        if args.subcommand == "commit":
            graphDrawer.commit(args.m)
        if args.subcommand == "add":
            graphDrawer.add(args.path)

    graphDrawer.generateHtml()


