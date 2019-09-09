# The MIT License (MIT)
# Copyright (c) 2016 Gerson Carlos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os

# Additional dependencies
from colorama import Fore, Style

# Constants
FILE_MODIFIED = 'modified'
FILE_NEW = 'new'
FILE_ADDED = 'added'
FILE_OUTDATED = 'outdated'
FILE_MERGING = 'merging'
FILE_MERGED = 'merged'
FILE_REMOVED = 'removed'


class FileStatus():
    def __init__(self):
        self.modified = []
        self.new = []
        self.added = []
        self.outdated = []
        self.merging = []
        self.merged = []
        self.removed = []

    def add_file(self, kind, filename):
        kind_list = getattr(self, kind)
        kind_list.append(filename)
        setattr(self, kind, kind_list)
    
    def print_files(self):
        if len(self.new) != 0:
            print("Untracked files:")
            print(" (use pycvs add <file>... to add them for commit)\n")
            for file in self.new:
                print(Fore.RED, "\t{0}".format(file))
            print(Style.RESET_ALL, "")
        if len(self.modified) != 0:
            print("Changes staged for commit:")
            print(" (use cvs commit... to check them in)\n")
            for file in self.modified:
                print(Fore.GREEN, "\tmodified:\t", end="")
                print("{0}".format(file))
            print(Style.RESET_ALL, "")
        if len(self.added) != 0:
            print("New files staged for commit:")
            print(" (use cvs commit... to check them in)\n")
            for file in self.added:
                if os.path.isfile(file.strip()):
                    print(Fore.RED, "\tnew file:\t", end=""),
                else:
                    print(Fore.RED, "\tnew directory:\t", end="")
                print("{0}".format(file))
            print(Style.RESET_ALL, "")
        if len(self.outdated) != 0:
            print("Outdated files:")
            print(" (use pycvs up <file>... to update them)\n")
            for file in self.outdated:
                print(Fore.CYAN, "\toutdated:\t", end="")
                print(file)
            print(Style.RESET_ALL, "")
        if len(self.merging) != 0:
            print("Changes that need to be merged before commit:")
            print(" (use pycvs up <file>... to update them)\n")
            for file in self.merging:
                print(Fore.CYAN, "\tto merge:\t", end="")
                print(file)
            print(Style.RESET_ALL, "")
        if len(self.merged) != 0:
            print("Files that had conflicts and need to be committed:")
            print(" (use cvs commit <file>... to check them in)\n")
            for file in self.merged:
                print(Fore.GREEN, "\tmerged:\t", end="")
                print("{0}".format(file))
            print(Style.RESET_ALL, "")
        if len(self.removed) != 0:
            print("Removed files staged for commit:")
            print(" (use cvs commit <file>... to check them in)\n")
            for filename in self.removed:
                print(Fore.YELLOW, "\tremoved:\t", end="")
                print(filename)
            print(Style.RESET_ALL, "")

        if (self.new == [] and self.modified == [] and self.added == []
            and self.merged == [] and self.removed == []):
            print("nothing to commit, working directory clean")