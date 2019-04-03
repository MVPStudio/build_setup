import yaml
import sys
import os
import subprocess
from shutil import copyfile, copytree
import argparse
import tempfile


def main():
    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'build_tag_push.py <docker_hub_name> '
                                     '<app_yml_path>')

    docker_hub_name = os.environ[str('DOCKER_REPO')]

    app_yml_path = ".mvpstudio/config.yml"

    data_from_app_yml = parse_app_file(app_yml_path)

    docker_login()

    build_docker_image(data_from_app_yml, app_yml_path)

    tag_docker_image(data_from_app_yml['name'], docker_hub_name)

    push_docker_image(data_from_app_yml['name'], docker_hub_name)


class BuildFailedException(Exception):
    def __init__(self, message):
        self.message = message


def parse_app_file(filename):
    '''
    This function is using the yaml built in to parse the file
    which can be done by searching for the key in the dictionary
    for the yaml file.
    '''
    with open(filename, "r") as file_contents:
        dict_of_contents = yaml.load(file_contents, Loader=yaml.FullLoader)

    return dict_of_contents

def docker_login():
    subprocess.check_call(["docker", "login", "-u" ,os.environ[str('DOCKER_LOGIN')], "-p", os.environ[str('DOCKER_PWD')]])

def create_context_directory(context_array, args_app_yml_path):
    '''
    Creating a directory that holds the docker contexts that were listed
    in their app.yml file.
    '''
    repo_root_path = os.path.dirname(app_yml_path)

    # skip temp directory if there is only a single docker context
    if (len(context_array) == 1):
        print(f'Found single docker context {context_array[0]} skipping temp dir')
        return os.path.join(repo_root_path, context_array[0])
    
    print(f'Creating a temporary directory containting {context_array}')

    docker_context_path = tempfile.mkdtemp()

    for file_or_dir in context_array:
        full_path = os.path.join(repo_root_path, file_or_dir)
        if os.path.isfile(full_path):
            copyfile(full_path, os.path.join(docker_context_path, file_or_dir))
        else:
            copytree(full_path, os.path.join(docker_context_path,
                            file_or_dir))

    return docker_context_path


def build_docker_image(data_from_app_yml, app_yml_path):
    '''
    Builds the docker image with the files that are in that directory,
    which should be a build, static, and Dockerfile. It is then named
    with their name from their app.yml file.
    '''
    print("Building the docker image for %s" % data_from_app_yml['name'])

    docker_dir_context = create_context_directory(data_from_app_yml
                                                  ['docker_context'],
                                                  app_yml_path)

    image_name = data_from_app_yml['name']

    subprocess.check_call(["docker", "build", docker_dir_context,
                     "-t", image_name])


def tag_docker_image(name_from_app_yml, docker_hub_name):
    '''
    This function is tagging the Docker Image with the namespace of the
    user which was passed in as the first argument, and the current git hash.
    '''
    subprocess.check_call(["docker", "tag", name_from_app_yml,
                    os.path.join(docker_hub_name,
                     name_from_app_yml)])

    current_hash = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%h"]).strip().decode('ascii')

    print("Tagging the docker image with the current hash", current_hash)

    subprocess.check_call(["docker", "tag", name_from_app_yml,
                    docker_hub_name + '/'+name_from_app_yml +
                    ':'+current_hash])


def push_docker_image(name_from_app_yml, docker_hub_name):
    '''
    This function is to push the docker image once it has been built and
    tagged with the name, and the commit hash tag, which is dependent on the
    functions build_DockerImage and tag_DockerImage functions.
    '''
    print("Pushing the docker image %s" % name_from_app_yml)

    subprocess.check_call(["docker", "push", docker_hub_name +
                    '/'+name_from_app_yml])


if __name__ == '__main__':
    main()
