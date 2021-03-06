import gitgraph
import sys
from typing import List
from string import Template
from os import listdir, path, urandom, remove
from graphviz import Digraph
from git import Repo
import shlex
import argparse
from shutil import copytree
from git import Repo, InvalidGitRepositoryError

class PushFailedException(Exception):
    """
    Exception raised when the command "push" fails.
    """
    def __init__(self, error_message):
        self.message = error_message
        super().__init__(error_message)

class GitGraphDrawer():
    def __init__(self):
        """
        Initialize a GitGraphDrawer object.
        """
        self.currentRepo = None
        self.count = 0

        copytree("/sources", "/locals")

        Repo.init("/remote", bare=True)

        try:
            for repo in [Repo(path.join("/locals", i)) for i in listdir("/locals")]:
                repo.create_remote("custom_remote", "/remote/")
        except InvalidGitRepositoryError:
            print("Un des dossiers proposé n'est pas un dépot git.")
            sys.exit(1)

        repo1 = Repo("/locals/git1") # TODO : add a way to specify the repo used as source for the newly created remote
        repo1.git.push("custom_remote", "main") 

    def push(self, branch: str) -> None:
        """
        Pushes on the branch gave in argument and raise an exception if failed.

        branch -- the branch on which we are pushing
        """
        remote = self.currentRepo.remote("custom_remote")
        summary = remote.push(branch)[0].summary
        hash_commit = remote.repo.head.commit.hexsha
        if len(summary.split("..")) > 1 and hash_commit.startswith(summary.split("..")[1].strip()):
            #push successful
            return
        else:
            #push failed :(
            raise PushFailedException(summary.strip())


    def change(self, gitName: str) -> None:
        """
        Changes the current local repo.

        gitName -- Indicates the new current local repo
        """
        self.currentRepo = Repo(path.join("/locals", gitName))
        self.currentRepo.config_writer().set_value("user", "name", "myusername").release()
        self.currentRepo.config_writer().set_value("user", "email", "myemail@localhost").release()

    def pull(self, remote_branch: str) -> None:
        """
        Pulls from the remote branch.

        remote_branch -- the remote branch from which we are pulling
        """
        self.currentRepo.git.pull("custom_origin", remote_branch)

    def render(self, startBranch=None, endBranch=None, failed=False) -> None:
        """
        Renders the current state of the all the branches (local and remote).

        startBranch -- if we have to draw an Arrow, the starting point
        endBranch -- the ending point of the arrow
        failed -- If we draw an error, is it red or blue
        """
        ggraph = gitgraph.GitGraph([path.join("/locals", i) for i in listdir("/locals")])
        ggraph.render(self.count, startBranch, endBranch, failed)

    def commit(self, commitMessage: str) -> None:
        """
        Commits changes to the current repo.

        commitMessage -- the message of the commit
        """
        self.currentRepo.git.commit(m=commitMessage)

    def add(self, pathToAdd: str) -> None:
        """
        Adds files to the staging area.
        If the file does not exist, it creates a empty file.
        If the file exists, it appends some random content in it.
        If the path is a directory, it creates an empty file with a random name.

        pathToAdd -- the relative path to a file or directory
        """
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

    def generateHtml(self, command_list: List[list]) -> None:
        """
        Generates the HTML animation from the template and all the generated dot files, with the list of commands.

        command_list -- list of commands
        """
        files_data = []

        for filename in listdir("/output"):
            if filename.endswith(".pdf"):
                continue
            if path.isdir(path.join("/output", filename)):
                continue

            with open(path.join("/output", filename), 'r') as f:
                file_data = f.read()
                files_data.append('`' + file_data.replace('`', '\\`') + '`')

        with open("template.html", "r") as f:
            template_str = f.read()
        
        data = ','.join(map(str, files_data))

        commands = []
        for i in command_list:
            commands.append('<br/>'.join(map(str, i)))

        for i in range(len(commands)):
            commands[i] = '`' + commands[i].replace('`', '\\`') + '`'



        render_commands = ','.join(map(str, commands))

        template = Template(template_str)
        output = template.substitute({"dots": data, "commands": render_commands})

        with open("/output/output.html", "w") as f:
            f.write(output)


if __name__ == '__main__':


    graphDrawer = GitGraphDrawer()

    with open("/commands.txt", "r") as f:
        commands = f.readlines()

    assert commands[0].startswith("change"), "The first command should be a change statement"

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='subcommand')

    parser_push = subparser.add_parser('push')
    parser_push.add_argument("repository", nargs='?', const="custom_remote", type=str, default="custom_remote")# à changer
    parser_push.add_argument("branch", nargs='?', const="main", type=str, default="main")

    parser_commit = subparser.add_parser('commit')
    parser_commit.add_argument("-m")

    parser_commit = subparser.add_parser('change')
    parser_commit.add_argument("branch_name")

    parser_commit = subparser.add_parser('add')
    parser_commit.add_argument("path")

    parser_commit = subparser.add_parser('render')

    command_list = []
    current_list = []


    for command_line in range(len(commands)):
        graphDrawer.count = command_line + 1

        command = commands[command_line]
        args = parser.parse_args(shlex.split(command))

        if args.subcommand == "push":


            target = None

            for branch in graphDrawer.currentRepo.remote("custom_remote").repo.branches:
                if branch.name == args.branch:
                    target = branch

            if target is None:
                print("push to non existant branch")
                sys.exit(1)

            current_list.append(command.strip())
            command_list.append(current_list)
            current_list = []

            try:
                graphDrawer.push(args.branch)
                graphDrawer.render(startBranch=graphDrawer.currentRepo.active_branch, endBranch=target, failed=False)
            except PushFailedException as e:
                graphDrawer.render(startBranch=graphDrawer.currentRepo.active_branch, endBranch=target, failed=True)




        if args.subcommand == "change":
            graphDrawer.change(args.branch_name)
        if args.subcommand == "render":
            graphDrawer.render()
            command_list.append(current_list)
            current_list = []
        if args.subcommand == "commit":
            graphDrawer.commit(args.m)
            current_list.append(command.strip())
        if args.subcommand == "add":
            graphDrawer.add(args.path)
            current_list.append(command.strip())

    graphDrawer.generateHtml(command_list)
