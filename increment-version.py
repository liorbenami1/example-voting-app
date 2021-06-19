#!/usr/bin/python3.6

from argparse import ArgumentParser
import subprocess
import os
import re
import sys
import yaml


def main() -> dict:
    """
    :brief: The Release utility script, currently - 2021-05-13 is automating the release procedure by executing the stages below:
    1. Checkout to target branch - git checkout "target_branch" e.g release/latest
    2. Reset target branch HEAD to origin source branch - e.g git reset --hard origin/master
    3. Tag commit with current version - e.g git tag vote_image_v0.10
    4. Push git tag to remote - e.g git push origin vote_image_v0.10
    5. push target branch - e.g git push
    6. checkout source branch - e.g git checkout source_branch
    7. increment source version
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

    parser.add_argument("-v", "--is_vote_change",  action='store_true', help="indicate if vote_image changed") #default='false'

    parser.add_argument("-r", "--is_result_change", action='store_true', help="indicate if image_result changed") #default='false'

    parser.add_argument("-w", "--is_worker_change", action='store_true', help="indicate if image_worker changed") #default='false'

    # Execute the parse_args() method
    args: NameSpace = parser.parse_args()
    # Change directory to where dev_values.yaml is located.
    os.chdir(args.path)

    # Checkout to target branch
    cmd: str = "git checkout " + args.target_branch
    print ("cmd = " + cmd)
    result: list = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Reset target branch to source branch
    cmd = "git reset --hard origin/" + args.source_branch
    print ("cmd = " + cmd)
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    # Read current versions from dev-values.yaml file
    version_info: dict = read_current_version()

    for key, value in version_info.items():
        if key == "image_vote" and args.is_vote_change or \
            key == "image_result" and args.is_result_change or \
            key == "image_worker" and args.is_worker_change or \
            key == "appVersion":
            tag: str = key + "_v" + value
            # Check if tag already exist
            cmd = "git tag -n " + tag
            print ("cmd = " + cmd)
            result = subprocess.getoutput(cmd)
            print ("result = " + result)
            # If tag not exist, create it
            if result == "":
                # Tag commit with current app versions
                cmd = "git tag " + tag
                print ("cmd = " + cmd)
                result = subprocess.getstatusoutput(cmd)
                error_check(result, cmd)

                # Push tag to remote
                cmd = "git push origin " + tag
                print ("cmd = " + cmd)
                result = subprocess.getstatusoutput(cmd)
                error_check(result, cmd)

                # Push target branch
                cmd = "git push"
                print ("cmd = " + cmd)
                result = subprocess.getstatusoutput(cmd)
                error_check(result, cmd)

    # Checkout to source branch
    cmd = "git checkout " + args.source_branch
    print ("cmd = " + cmd)
    result = subprocess.getstatusoutput(cmd)
    error_check(result, cmd)

    for key, value in version_info.items():
        if key == "image_vote" and args.is_vote_change or \
            key == "image_result" and args.is_result_change or \
            key == "image_worker" and args.is_worker_change or \
            key == "appVersion":

            if args.update == '':
                # Increment source version
                current_version = increment_version(key, value, args.increment)
            else:
                # Update source version
                current_version = increment_version(key, value, args.update)

            # Add and commit change to source_branch
            cmd = "git add dev-values.yaml"
            print ("cmd = " + cmd)
            result = subprocess.getstatusoutput(cmd)
            error_check(result, cmd)

            commit_message: str = key + " :: incremented to " + key + "_v"  + current_version
            cmd = "git commit -a -m " + "\"" + commit_message + "\""
            print ("cmd = " + cmd)
            result = subprocess.getstatusoutput(cmd)
            error_check(result, cmd)

            # Push changes to source_branch
            cmd = "git push"
            print ("cmd = " + cmd)
            result = subprocess.getstatusoutput(cmd)
            error_check(result, cmd)

    # print current version to curr_ver.yaml (new file)
    with open("curr_ver.yaml", "w+") as file:
        yaml.dump(version_info, file, default_flow_style=False)

def read_current_version() -> dict:
    """
    :brief: read current version ("image_vote", "image_result", "image_worker", "appVersion").
    :return: dict, current version for each ("image_vote", "image_result", "image_worker", "appVersion")
    """
    with open("dev-values.yaml", "r") as dev_values:
        values_list = yaml.load(dev_values)
        dict_ver = {}
    for key, value in values_list.items():
        if key in ("image_vote", "image_result", "image_worker", "appVersion"):
            ver = value.get('tag')
            print (str(key) + " : " + str(ver))
            dict_ver[key] = ver

    print (dict_ver)
    return dict_ver

def increment_version(image_name: str, current_version: str, increment: str) -> str:
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
               "read_dev_values = " + read_dev_values.get(image_name).get('tag'))
        read_dev_values.get(image_name)['tag'] = increment
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
