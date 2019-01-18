import yaml
import sys
import os
import subprocess
from shutil import copyfile
import argparse

# python3 build_tag_push.py namesapce app_yaml_path

# User input for the docker namespace. Refer to this as args.variable

parser = argparse.ArgumentParser(description='Docker namespace')
parser.add_argument('docker_hub_name', type=str, help='DockerHub namespace')
# parser.add_argument('docker_hub_password',
#                     type=str, help='DockerHub password')
parser.add_argument('app_yml_path', type=str,
                    help='Repository path to MVP Studio file')

args = parser.parse_args()


def main():
    filename = args.app_yml_path
    data_from_app_yml = parse_app_file(filename)
    create_context_directory(data_from_app_yml['docker_context'])
    build_check_app(data_from_app_yml)
    build_docker_image(data_from_app_yml)
    tag_docker_image(data_from_app_yml['name'])
    push_docker_image(data_from_app_yml['name'])


def parse_app_file(filename):
    '''
    This function is using the yaml built in to parse the file
    which can be done by searching for the key in the dictionary
    for the yaml file.

    Contents (include in the README):

    name = dict_of_contents['name']
    build_script = dict_of_contents['build']
    test_call = dict_of_contents['test']
    docker_context_build = dict_of_contents['docker_context'][0]
    docker_context_static = dict_of_contents['docker_context'][1]
    '''
    with open(filename, "r") as file_contents:
        dict_of_contents = yaml.load(file_contents)

    return dict_of_contents


def build_check_app(data_from_app_yml):
    '''
    This is building and testing their app. Ignoring the return code.
    '''
    os.chdir(os.path.dirname(args.app_yml_path))
    subprocess.call(['bash', data_from_app_yml['build']])
    subprocess.call(['bash', data_from_app_yml['test']])
    # QUESTION: I know you guys mentioned needing to ignore any failures
    # running their test cases might cause, but how should I do this?


def create_context_directory(contextArray):
    '''
    Creating a directory that holds the docker contexts that were listed
    in their app.yml file. This includes their build and static files.
    Note: This directory still needs a DockerFile in it, which I am assuming
    we will need to provide for them to use as a base file, and that
    would need copied into this directory too, so that is what I did via the
    last copyfile command as the end of this function.
    '''
    repo_root_path = os.path.dirname(args.app_yml_path)
    dir_name = "docker_context"
    os.makedirs(repo_root_path+'/'+dir_name, exist_ok=True)

    docker_context_path = repo_root_path+'/'+dir_name

    copyfile(repo_root_path+'/'+contextArray[0],
             docker_context_path+'/'+contextArray[0])

    copyfile(repo_root_path+'/'+contextArray[1],
             docker_context_path+'/'+contextArray[1])

    copyfile(repo_root_path+'/Dockerfile', docker_context_path+'/Dockerfile')

    return docker_context_path


def build_docker_image(data_from_app_yml):
    '''
    Builds the docker image with the files that are in that directory,
    which should be a build, static, and Dockerfile. It is then named
    with their name from their app.yml file.
    '''
    docker_dir_context = create_context_directory(data_from_app_yml
                                                  ['docker_context'])

    image_name = data_from_app_yml['name']

    subprocess.check_call(["docker", "build", docker_dir_context,
                           "-t", image_name])


def tag_docker_image(name_from_app_yml):
    '''
    This function is tagging the Docker Image with the namespace of the
    user which was passed in as the first argument, and the current git hash.

    Note: The current git hash is shortened a bit, but to display the full
    hash, then change the lower case %h to upper case %H. Also, this is
    decoded via ASCII due to the output being in bytes.

    The source for this command is:
    https://container-solutions.com/tagging-docker-images-the-right-way
    '''

    subprocess.check_call(["docker", "tag", name_from_app_yml,
                           args.docker_hub_name+'/'+name_from_app_yml])

    current_hash = subprocess.check_output(["git", "log", "-1",
                                            "--pretty=%h"]).strip().decode(
                                            'ascii')
    # print(current_hash)
    subprocess.check_call(["docker", "tag", name_from_app_yml,
                           args.docker_hub_name +
                           '/'+name_from_app_yml +
                           ':'+current_hash])

    # QUESTION: Did we come up with a verdict on whether or not we are doing
    # an additional version number tag? If so, do you have any recommendations
    # on how I should do this? I have been researching it a bit and haven't
    # seen anything that looks like what you are wanting.


def push_docker_image(name_from_app_yml):
    '''
    This function is to push the docker image once it has been built and
    tagged with the name, and the commit hash tag, which is dependent on the
    functions build_DockerImage and tag_DockerImage functions.
    '''
    subprocess.check_call(["docker", "push", args.docker_hub_name +
                          '/'+name_from_app_yml])


if __name__ == '__main__':
    main()

# Comments regarding testing:
# I have not created unit tests for this yet, I am just testing it all
# manually through test files I have made, and calling it all in main.
# My next step is to learn about unit tests and implement them.
