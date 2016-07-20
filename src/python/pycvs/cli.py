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

# Common python packages
import sys
import getpass
import json
import os.path
import re
import shutil
import pydoc

# Additional dependencies
import pexpect
from colorama import Fore, Style


class PyCvs():
    """
    Main class for pycvs project.
    """
    CONFIGURATON_FILE = os.path.expanduser("~/.pycvs")

    def __init__(self):
        """
        Initalize class loading the credentials from the configuration file.
        """
        if shutil.which("cvs") is None:
            print("Could not find cvs installation")
            exit(1)

        self.credentials = {}

        if not os.path.isfile(self.CONFIGURATON_FILE):
            print("No configuration file found at {0}"
                  .format(self.CONFIGURATON_FILE))

            self.credentials["user"] = input("User: ")
            self.credentials["password"] = getpass.getpass()
            self.credentials["root"] = input("CVS Root: ")
            with open(self.CONFIGURATON_FILE, "w") as cfg_file:
                json.dump(self.credentials, cfg_file, indent=4)
        else:
            with open(self.CONFIGURATON_FILE, "r") as cfg_file:
                self.credentials = json.load(cfg_file)

    def _access_cvs(self, cmd):
        """
        Spawn the CVS command and login the user. Also check whether the
        password was accept.

        Args:
            cmd(str): CVS command to be spawned.

        Returns:
            A pexpect object containing the CVS session.
        """
        cvs_obj = pexpect.spawn(cmd)
        cvs_obj.timeout = 300
        value = cvs_obj.expect([pexpect.EOF, "password"])
        if value == 1:
            cvs_obj.sendline(self.credentials['password'])

        value = cvs_obj.expect([pexpect.EOF, "Permission denied"])
        if value == 1:
            print("Invalid password for {0} (~/.pycvs)"
                  .format(self.credentials["user"]))
            return None

        return cvs_obj

    def _checkout(self, args):
        """
        Checks out the repository. Prints a resume of the checkout -- number
        of files and directories.
        """
        repo = args.pop()
        opts = " ".join(args)
        print("Checking out repository {0}".format(repo))

        spawn_str = "cvs -d {0} co {2} {1}".format(self.credentials['root'],
                                                   repo,
                                                   opts)
        cvs_obj = self._access_cvs(spawn_str)
        if cvs_obj is not None:
            output = cvs_obj.before.decode("utf-8")
            output = output.split("\n")
            files = 0
            dirs = 0
            for line in output:
                if line.startswith("U "):
                    files += 1
                elif line.startswith("cvs server: Updating"):
                    dirs += 1

            print("")
            print("{0} files checked out".format(str(files)))
            print("{0} directories checked out".format(str(dirs)))

    def _update(self, args=[]):
        """
        Run the CVS update command in the current working directory.

        Args:
            args(list): Command line arguments list. Defaults to []
        """
        if os.path.isfile("CVS/Repository"):
            with open("CVS/Repository", "r") as repo_file:
                lines = repo_file.readlines()
            current_dir = lines[0].strip()
        else:
            print("Not in a CVS repository")
            exit(1)
        opts = " ".join(args)
        print("Updating from {0}".format(current_dir))
        print("")

        spawn_str = "cvs up {0}".format(opts)
        cvs_obj = self._access_cvs(spawn_str)
        if cvs_obj is not None:
            output = cvs_obj.before.decode("utf-8")
            output = output.split("\n")
            files = 0
            conflicts = 0

            for line in output:
                if line.startswith("U "):
                    files += 1
                elif line.startswith("C "):
                    conflicts += 1
                    filename = re.match("C (.*)\s", line).group(1)
                    print("Conflict on file {0}".format(filename))

            print("")
            if files > 0:
                print("{0} files updated".format(str(files)))
            if conflicts > 0:
                print("{0} conflicted files".format(str(conflicts)), end="")
                print(" (solve them before commit!)")

    def _status(self):
        """
        Get cvs status from the server and print and beautyful output
        (yeah, git style).
        """
        if os.path.isfile("CVS/Tag"):
            with open("CVS/Tag", "r") as tag_file:
                lines = tag_file.readlines()
            line = lines[0]
            if line.startswith("N"):
                print("On tag {0}".format(line.strip("N\n")))
            elif line.startswith("T"):
                print("On branch {0}".format(line.strip("T\n")))
        else:
            print("On branch HEAD")

        spawn_str = "cvs status"

        cvs_obj = self._access_cvs(spawn_str)
        if cvs_obj is not None:
            output = cvs_obj.before.decode("utf-8")
            output = output.split('\n')

            modified = []
            new = []
            added = []
            outdated = []
            merging = []
            current_dir = ""

            for line in output:
                match_file = re.match("File: (.*)\s+Status: (.*)\s", line)
                match_dir = re.match(".*Examining (.*)\s", line)
                match_new = re.match("\?\s+(.*)\s", line)
                if match_file is not None:
                    if match_file.group(2) == "Locally Modified":
                        modified.append(current_dir + match_file.group(1))
                    elif match_file.group(2) == "Locally Added":
                        added.append(current_dir + match_file.group(1))
                    elif match_file.group(2) == "Needs Patch":
                        outdated.append(current_dir + match_file.group(1))
                    elif match_file.group(2) == "Needs Merge":
                        merging.append(current_dir + match_file.group(1))
                elif match_dir is not None:
                    current_dir = match_dir.group(1) + '/'
                elif match_new is not None:
                    new.append(match_new.group(1))

            if len(new) != 0:
                print("Untracked files:")
                print(" (use pycvs add <file>... to add them for commit)\n")
                for file in new:
                    print(Fore.RED, "\t{0}".format(file))
                print(Style.RESET_ALL, "")
            if len(modified) != 0:
                print("Changes staged for commit:")
                print(" (use cvs commit... to check them in)\n")
                for file in modified:
                    print(Fore.GREEN, "\tmodified:\t", end="")
                    print("{0}".format(file))
                print(Style.RESET_ALL, "")
            if len(added) != 0:
                print("New files staged for commit:")
                print(" (use cvs commit... to check them in)\n")
                for file in added:
                    if os.path.isfile(file.strip()):
                        print(Fore.RED, "\tnew file:\t", end=""),
                    else:
                        print(Fore.RED, "\tnew directory:\t", end="")
                    print("{0}".format(file))
                print(Style.RESET_ALL, "")
            if len(outdated) != 0:
                print("Outdated files:")
                print(" (use pycvs up <file>... to update them)\n")
                for file in outdated:
                    print(Fore.CYAN, "\toutdated:\t", end="")
                    print(file)
                print(Style.RESET_ALL, "")
            if len(merging) != 0:
                print("Changes that need to be merged before commit:")
                print(" (use pycvs up <file>... to update them)\n")
                for file in merging:
                    print(Fore.CYAN, "\tto merge:\t", end="")
                    print(file)
                print(Style.RESET_ALL, "")

            if new == [] and modified == [] and added == []:
                print("nothing to commit, working directory clean")

    def _add(self, args):
        """
        Add the given files to CVS server, in order to be committed later on.

        Args:
            args(list): the list of files from the command line
        """
        # TODO: handle special case to add *
        for to_add in args:
            spawn_str = "cvs add {0}".format(to_add)
            cvs_obj = self._access_cvs(spawn_str)
            if cvs_obj is not None:
                output = cvs_obj.before.decode("utf-8")
                output = output.split('\n')

                if os.path.isfile(to_add):
                    for line in output:
                        match = re.match(".* scheduling file `(.*)'.*", line)
                        if match is not None:
                            print("\tstaging {0} to commit"
                                  .format(match.group(1)))
                elif not to_add.endswith("CVS"):
                    for line in output:
                        match = re.match("Directory .* to the repository.*",
                                         line)
                        if match is not None:
                            print("Directory {0} added".format(to_add))
                    files = os.listdir(to_add)
                    files = map(lambda x: "{0}/{1}".format(to_add, x), files)
                    self._add(files)

    def _diff(self, args):
        """
        Found the diff between revisions.

        Args:
            args(list): Command line arguments for diff
        """
        # I do like unified diff syntax
        if "-u" not in args:
            args.insert(0, "-u")

        opts = " ".join(args)
        spawn_str = "cvs diff {0}".format(opts)
        cvs_obj = self._access_cvs(spawn_str)
        if cvs_obj is not None:
            output = cvs_obj.before.decode("utf-8")
            output = output.split("\n")
            output = filter(lambda x: "cvs server:" not in x, output)
            output_colored = []
            for line in output:
                if line.startswith("+") and not line.startswith("+++"):
                    line = Fore.GREEN + line
                elif line.startswith("-") and not line.startswith("---"):
                    line = Fore.RED + line
                elif line.startswith("@@"):
                    line = Fore.CYAN + line
                output_colored.append(line)
            pydoc.pipepager("\n".join(output_colored), cmd="less -R")

    def process(self):
        """
        Process the user input.
        """
        try:
            command = sys.argv[1]
        except IndexError:
            print("Nothing to do")
        else:
            if command == "checkout" or command == "co":
                try:
                    self._checkout(sys.argv[2:])
                except IndexError:
                    print("Missing arguments for {0} command".format(command))
            elif command == "status":
                self._status()
            elif command == "add":
                try:
                    self._add(sys.argv[2:])
                except IndexError:
                    print("Missing arguments for {0} command".format(command))
            elif command == "update" or command == "up":
                try:
                    self._update(sys.argv[2:])
                except IndexError:
                    self._update()
            elif command == "diff":
                try:
                    self._diff(sys.argv[2:])
                except IndexError:
                    print("Missing diff parameters")
            else:
                print("Unknown command {0}".format(command))
