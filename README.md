# GitGraph

This project aims to generate dot files and pdf formats of git repositories states as well as animations of the states of git trees.

## Usage 

`docker build -t gitgraph .`

`docker run -v </path/to/repo1>:/sources/git1 -v </path/to/repo2>:/sources/git2 -v </path/to/commands.txt>:/commands.txt -v </output/folder>:/output gitgraph`

The output directory must be empty. Git repositories on the host machine are left unmodified.

Example commands.txt with currently supported commands :

```
change git1
add .
commit -m "Hello from local1"
render
push
render
change git2
add .
commit -m "Hello from local2"
render
push
render
```

## Commands details

- `change [directory]` : Sets the current working directory to directory. Must be the first command in commands.txt. Must be a git repository in `/sources`.

- `add [directory or file]` : Adds a file or a directory to the staging area, modifications to the file or directory will be done automatically.

- `render` : Saves the current state of the git repositories in a dot file and a pdf format. It will be included in the final animation. The `push `  command automatically does a `render` operation.

- The following git commands are available : 

```
add [directory or file] 
commit -m [message]
push [target branch (default main)]
```
