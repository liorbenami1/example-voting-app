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

    # Read current version from dev-values.yaml file
    version_info: str = read_current_version()

    #current_version: dict = version_info
   # max_ver = max(version_info.values())
    #print ("max_ver = " + max_ver)

    # Tag commit with current app versions
    cmd = "git tag v" + version_info
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Push tag to remote
    cmd = "git push origin v" + version_info
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
        current_version = increment_version(version_info, args.increment)
    else:
        # Update source sysyroot_sdk project version
        current_version = increment_version(version_info, args.update)

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

def read_current_version() -> str:
    """
    :brief: read current sysyroot_sdk version.
    :return: string, current sysyroot_sdk version
    """
    with open("dev-values.yaml", "r") as dev_values:
        values_list = yaml.load(dev_values)
        dict_ver = {}
    for key, value in values_list.items():
        if key in ("image_vote"): #, "image_result", "image_worker"):
            ver = value.get('tag')
            print (str(key) + " : " + str(ver))
            dict_ver[key] = ver

    print (dict_ver)


    #main_sysroot_str = dev_values.read()
    #current_version: str = re.findall("sysroots_sdk_version=(\"\d+\.\d+\.\d+\")", main_sysroot_str)[0]
    #current_version = current_version.strip('"');
    #version_info: str = current_version
    #return version_info
    return ver




def increment_version(current_version: str, increment: str) -> str:
    """
    :brief: increment app version.
    :param: current_version - current app version
    :param: increment - number to add to minor part of the current version
    :example: number - 2, 2+ 0.1.40(current version) = 0.1.42
    :return: string, current incremented app version.
    """
    with open("dev-values.yaml", "r") as dev_values:
        read_dev_values: dict = yaml.load(dev_values)

    with open("dev-values.yaml", "w+") as dev_values:
        # Incrementing version by value e.g 1
        version_list: list = current_version.split('.')
        version_list[-1] = str(int(version_list[-1]) + int(increment))
        increment = '.'.join(version_list)

        # substitute new version with the old one.
        print ("current_version = " + current_version + "\n"
               "increment = " + increment + "\n"
               "read_dev_values = " + read_dev_values.get('image_vote').get('tag'))
        read_dev_values.get('image_vote')['tag'] = increment
        yaml.dump(read_dev_values, dev_values, default_flow_style=False)
        #read_dev_values = re.sub(current_version, increment, read_dev_values.get[0].get('tag'))
        #dev_values.write(read_dev_values)

    return increment

def error_check(result: str, cmd: str):
    """
    :brief: check the command result for errors, if error occur script is aborted
    """
    if result[0] != 0:
        print(cmd + " failed \n" + result[1])
        sys.exit()


if __name__ == "__main__":
    main()
