#!/usr/bin/python3.6

from argparse import ArgumentParser
import subprocess
import os
import re
import sys
import yaml


def main():
    """
    :brief: The Release utility script, currently - 2021-05-13 is automating the  sysroot release procedure by executing the stages below:
    1. Checkout to target branch - git checkout "target_branch" e.g release/sysroot
    2. Reset target branch HEAD to origin source branch - e.g git reset --hard origin/master
    3. Tag commit with current sysroot  version - e.g git tag v0.0.53
    4. Push git tag to remote - e.g git push origin v0.0.52
    5. push target branch - e.g git push
    6. checkout source branch - e.g git checkout source_branch
    7. increment source sysroot version
    8. add and commit change to source_branch
    9. push changes to source_branch.

    """
    # Create the parser
    parser: ArgumentParser = ArgumentParser()

    # restrict arguments that can't be used at the same time e.g --increment and --update
    group: _MutuallyExclusiveGroup = parser.add_mutually_exclusive_group()

    # Add the arguments
    group.add_argument("-i", "--increment", type=str, help="increment version"
                                                           " by adding a number to the minor part of the version",
                       default='1')

    group.add_argument("-u", "--update", type=str, help="update the version", default='')

    parser.add_argument("-p", "--path", type=str, help="work directory path", required=True)

    parser.add_argument("-s", "--source_branch", type=str, help="e.g master branch", required=True)

    parser.add_argument("-t", "--target_branch", type=str, help="e.g release/latest branch", required=True)

    # Execute the parse_args() method
    args: NameSpace = parser.parse_args()
    # Change directory to where create_sysroot_sdk.sh is located.
    os.chdir(args.path)

    # Checkout to target branch
    cmd: str = "git checkout " + args.target_branch
    result: list = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Reset target branch to source branch
    cmd = "git reset --hard origin/" + args.source_branch
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    version_info: str = read_current_version()
    # Read current version from create_sysroot_sdk.sh file
    current_version: str = version_info

"""
    # Tag commit with current sysroot_sdk version
    cmd = "git tag v" + current_version
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Push tag to remote
    cmd = "git push origin v" + current_version
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Push target branch
    cmd = "git push"
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Checkout to source branch
    cmd = "git checkout " + args.source_branch
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    if args.update == '':
        # Increment source sysyroot_sdk  version
        current_version = increment_version(current_version, args.increment)
    else:
        # Update source sysyroot_sdk project version
        current_version = increment_version(current_version, args.update)

        # Add and commit change to source_branch
        cmd = "git add dev-values.yaml"
        result = subprocess.getstatusoutput(cmd)
        error_check(result, cmd)

    commit_message: str = " vote :: incremented to v" + current_version
    cmd = "git commit -a -m " + "\"" + commit_message + "\""
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Push changes to source_branch
    cmd = "git push"
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)
"""

def read_current_version() -> str:
    """
    :brief: read current sysyroot_sdk version.
    :return: string, current sysyroot_sdk version
    """
    with open("dev-values.yaml", "r") as dev_values:
        values_list = yaml.load(dev_values, loader=yaml.FullLoader)
    for key, value in values_list.items():
        print (key + " : " + str(value))
        #main_sysroot_str = dev_values.read()
    #current_version: str = re.findall("sysroots_sdk_version=(\"\d+\.\d+\.\d+\")", main_sysroot_str)[0]
    #current_version = current_version.strip('"');
    #version_info: str = current_version
    #return version_info
    return "0.88"



'''
def increment_version(current_version: str, increment: str) -> str:
    """
    :brief: increment sysyroot_sdk version.
    :param: current_version - current sysyroot_sdk version
    :param: increment - number to add to minor part of the current version
    :example: number - 2, 2+ 0.1.40(current version) = 0.1.42
    :return: string, current incremented sysyroot_sdk version.
    """
    with open("create_sysroot.sh", "r") as main_sysroot_fd:
        main_sysroot: str = main_sysroot_fd.read()

    with open("create_sysroot.sh", "w+") as main_sysroot_fd:
        # Incrementing version by value e.g 1
        version_list: list = current_version.split('.')
        version_list[-1] = str(int(version_list[-1]) + int(increment))
        increment = '.'.join(version_list)

        # substitute new version with the old one.
        main_sysroot = re.sub(current_version, increment, main_sysroot)
        main_sysroot_fd.write(main_sysroot)

    return increment

def update_version(from_version: str, to_version: str) -> str:
    """
    :brief: increment sysyroot_sdk version.
    :param: from_version - current sysyroot_sdk version
    :param: to_version - new version to update
    :return: string, new sysyroot_sdk version.
    """
    with open("create_sysroot.sh", "r") as main_sysroot_fd:
        main_sysroot: str = main_sysroot_fd.read()

    with open("create_sysroot.sh", "w+") as main_sysroot_fd:
        # Incrementing version by value e.g 1
        version_list: list = from_version.split('.')
        version_list[-1] = str(int(version_list[-1]) + int(to_version))
        to_version = '.'.join(version_list)

        # substitute new version with the old one.
        main_sysroot = re.sub(from_version, to_version, main_sysroot)
        main_sysroot_fd.write(main_sysroot)

    return to_version
'''

def error_check(result: str, cmd: str):
    """
    :brief: check the command result for errors, if error occur script is aborted
    """
    if result[0] != 0:
        print(cmd + " failed \n" + result[1])
        sys.exit()


if __name__ == "__main__":
    main()
