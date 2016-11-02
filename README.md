# pycvs
A python client for CVS repositories.

Yeah, I know that CVS is a hundred years old, but sometimes you are stick to work with it. This utility is your best buddy to help you out! :)

### Advantages
* No password prompting
* Beautiful output
* Recursive addition

## Dependencies

It runs only on Python 3 and depends on some libraries (available at PyPI):

* pexpect>=4.1.0
* colorama>=0.3.7


## Installation

To install the package from the source:

    python setup.py install

Or to install form the PyPI (soon):

    pip install pycvs

In both options the command pycvs will be available from the command line.

## Supported commands

This contains the current supported commands:

Checkout a brand new repository or update an existing one:

    % pycvs checkout <repo>
    Checking out repository repo

    385 files checked out
    70 directories checked out

    % pycvs update <repo>

Get current status of a repository:

    % cd my_repo
    % pycvs status
    On branch HEAD
    Untracked files:
     (use cvs add <file>... to add them for commit)

      	bla

    Changes staged for commit:
     (use cvs commit... to check them in)

    	./my_script.py

Add new files to repository. It works recursively:

    % cd my_repo
    % pycvs add foo/
    Directory foo added
    	staging foo/bla to commit
    	staging foo/ble to commit

Diff the modified files from the server:

    % pycvs diff [parameters]
    (open a less windows with the differences in the unified syntax and colors)

Log the file history from the server:

    % pycvs log [parameters]
    (open a less windown with file's revisions, tags...)
