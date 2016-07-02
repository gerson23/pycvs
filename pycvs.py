import pexpect
import sys
import getpass
import json
import os.path
import re


class PyCvs():
    """
    Main class for pycvs project.
    """
    CONFIGURATON_FILE = os.path.expanduser("~/.pycvs")

    def __init__(self):
        """
        Initalize class loading the credentials from the configuration file.
        """
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

    def _checkout(self, repo):
        print("Checking out repository {0}".format(repo))

        spawn_str = "cvs -d {0} co {1}".format(self.credentials['root'],
                                               repo)
        cvs_obj = pexpect.spawn(spawn_str)
        cvs_obj.timeout = 300
        value = cvs_obj.expect(["password"])
        if value == 0:
            cvs_obj.sendline(self.credentials['password'])

        value = cvs_obj.expect([pexpect.EOF])
        if value == 0:
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

    def _status(self):
        print("Getting status from current repository")

        spawn_str = "cvs status"

        cvs_obj = pexpect.spawn(spawn_str)
        cvs_obj.timeout = 300
        value = cvs_obj.expect(["password"])
        if value == 0:
            cvs_obj.sendline(self.credentials['password'])

        value = cvs_obj.expect([pexpect.EOF])
        if value == 0:
            output = cvs_obj.before.decode("utf-8")
            output = output.split('\n')

            modified = []
            new = []
            current_dir = ""

            for line in output:
                match_file = re.match("File: (.*)\s+Status: (.*)\s", line)
                match_dir = re.match(".*Examining (.*)\s", line)
                match_new = re.match("\?\s+(.*)\s", line)
                if match_file is not None:
                    if match_file.group(2) == "Locally Modified":
                        modified.append(current_dir + match_file.group(1))
                elif match_dir is not None:
                    current_dir = match_dir.group(1) + '/'
                elif match_new is not None:
                    new.append(match_new.group(1))

            if len(new) != 0:
                print("Untracked files:")
                print(" (use cvs add <file>... to add them for commit)\n")
                for file in new:
                    print("\t{0}".format(file))
                print("")
            if len(modified) != 0:
                print("Changes staged for commit:")
                print(" (use cvs commit... to check them in)\n")
                for file in modified:
                    print("\t{0}".format(file))
                print("")

    def process(self):
        command = sys.argv[1]
        if command == "checkout" or command == "co":
            self._checkout(sys.argv[2])
        if command == "status":
            self._status()

if __name__ == "__main__":
    pycvs = PyCvs()
    pycvs.process()
