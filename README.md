# GitGraph
- Usage :
`docker build -t gitgraph .`

`docker run -v </path/to/repo1>:/sources/git1 -v </path/to/repo2>:/sources/git2 -v </path/to/commands.txt>:/commands.txt -v </output/folder>:/output gitgraph`

Example commands.txt with currently supported commands
```
switch git1
add .
commit -m "bobcat"
render
```
