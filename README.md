# pycvs
A python client for CVS repositories.

Yeah, I know that CVS is a hundred years old, but sometimes you are stick to work with it. This utility is your best buddy to help you out! :)


Dependencies
------------

It runs only on Python 3 and depends on some libraries (available at PyPi):

* pexpect>=4.*


Supported commands
------------------

This contains the current supported commands:

Checkout a brand new repository:
    % ./pycvs.py checkout <repo>
    Checking out repository repo

    385 files checked out
    70 directories checked out

Get current status of a repository:
    % cd my_repo
    % ./pycvs.py status
    On branch HEAD
    Untracked files:
     (use cvs add <file>... to add them for commit)

      	bla

    Changes staged for commit:
     (use cvs commit... to check them in)

    	./my_script.py
