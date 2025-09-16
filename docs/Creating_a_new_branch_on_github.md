## Creating a branch

We can create a branch without having the permission to write , which is required only to push a branch.

So if we want to have a branch in a particular repository in github, we need a cloned copy of that directory in our system

Now on the command line , do a DIR or LS to show us what files are in that.

Well, we're creating a branch, so we do a **`git branch <name of the new branch`>**.

So we now are on that and anything we do stays in that. So it's quite safe.

## Adding a file

So, let's say that we add a file there. We need to save the file in the cloned repository on our system in the desired file as a `.txt file`(or a normal text file on windows). It should be ensured that the file name cotains no spaces. Eg. - *biogeochemical_cycles* and not *biogeochemical cycles*.

So back on the command line, we do a **`git checkout <new branch name>`**
and then , a **` git status`**. We should be able to see the file name at the bottom.

So now we have got a file on our machine,  which is now part of the Amylib directory but it's not yet part of the git system because we've got to commit it.

The file should be under the list of untracked files  because git doesn't know about it at the moment. It knows the file is there, but it's not part of the repositor

So what we're going to do is add it. So we say **`git add <file_name.txt>`**

Now if we do **`git status`** again, we should be able to see the file (in green) at the top.

What weve done is we have told Git, about a file which we want Git to look after. That's what `git add` does. It says here's a file, look after it. So git has got a new file but we have not committed it. It's on the system. We want it to be pushed somewhere but we can't push it until we commit it.

## Committing a file

So now we say **`git commit -am "added file_name.txt`**.

So we have now made a commit. It's on the machine, but it's not, been put to GitHub. Now the 1st time we do it, we have to tell Git that something's coming. So, we do **`git push --set-upstream origin <new branch name>`**. The file gets committed to the repository on git hub only if you are a collaborator (i.e, you have permission fromthe administrator).

## Permission from the administrator

To add people as collaborator, the admiistrator find settings on his/her github account and adds people as collaborators.

We get an email from github regarding being a collaborator and accept the invitation to contribute to the repository.

So now, that we have the permission, we go back to our command line and issue the same command , we will have a new branch with the added file on github.

