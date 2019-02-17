import yaml
import sys
import os
import subprocess
import shutil
from shutil import copyfile
import argparse
import tempfile


def main():
    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'build_tag_push.py <docker_hub_name> '
                                     '<app_yml_path>')

    parser.add_argument('docker_hub_name', type=str,
                        help='DockerHub namespace')

    parser.add_argument('app_yml_path', type=str,
                        help='Repository path to MVP Studio file')

    parser.add_argument('--ignore_test_errors', type=bool,
                        help='Boolean value if you want to ignore'
                        'test errors.')

    args = parser.parse_args()

    data_from_app_yml = parse_app_file(args.app_yml_path)

    build_check_app(data_from_app_yml, args.app_yml_path,
                    args.ignore_test_errors)

    build_docker_image(data_from_app_yml, args.app_yml_path)

    tag_docker_image(data_from_app_yml['name'], args.docker_hub_name)

    push_docker_image(data_from_app_yml['name'], args.docker_hub_name)


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
        dict_of_contents = yaml.load(file_contents)

    return dict_of_contents


def build_check_app(data_from_app_yml, args_app_yml_path,
                    args_ignore_test_errors):
    '''
    This is building and testing their app. Ignoring the return code.
    '''
    path_to_build_and_test = args_app_yml_path
    os.chdir(os.path.dirname(path_to_build_and_test))

    print("Starting build task: %s" % data_from_app_yml['build'])

    build_res = subprocess.call(['bash', data_from_app_yml['build']])

    if build_res != 0:
        raise BuildFailedException('The build failed.')

    print("Starting test task: %s" % data_from_app_yml['test'])

    result = subprocess.call(['bash', data_from_app_yml['test']])

    if result != 0:
        if args_ignore_test_errors:
            print("ERROR: Tests failes.")
        else:
            raise RunTimeError('Unit tests failed.')


def create_context_directory(context_array, args_app_yml_path):
    '''
    Creating a directory that holds the docker contexts that were listed
    in their app.yml file.
    '''
    print(f'Creating a temporary directory containting {context_array}')

    repo_root_path = os.path.dirname(args_app_yml_path)

    docker_context_path = tempfile.mkdtemp()

    for file_or_dir in context_array:
        full_path = os.path.join(repo_root_path, file_or_dir)
        if os.path.isfile(full_path):
            copyfile(full_path, os.path.join(docker_context_path, file_or_dir))
        else:
            shutil.copytree(full_path, os.path.join(docker_context_path,
                            file_or_dir))

    return docker_context_path


def build_docker_image(data_from_app_yml, args_app_yml_path):
    '''
    Builds the docker image with the files that are in that directory,
    which should be a build, static, and Dockerfile. It is then named
    with their name from their app.yml file.
    '''
    print("Building the docker image for %s" % data_from_app_yml['name'])

    docker_dir_context = create_context_directory(data_from_app_yml
                                                  ['docker_context'],
                                                  args_app_yml_path)

    image_name = data_from_app_yml['name']

    subprocess.call(["docker", "build", docker_dir_context,
                     "-t", image_name])


def tag_docker_image(name_from_app_yml, args_docker_hub_name):
    '''
    This function is tagging the Docker Image with the namespace of the
    user which was passed in as the first argument, and the current git hash.
    '''
    subprocess.call(["docker", "tag", name_from_app_yml,
                    os.path.join(args_docker_hub_name,
                     name_from_app_yml)])

    current_hash = subprocess.check_output(
        ["git", "log", "-1", "--pretty=%h"]).strip().decode('ascii')

    print("Tagging the docker image with the current hash", current_hash)

    subprocess.call(["docker", "tag", name_from_app_yml,
                    args_docker_hub_name + '/'+name_from_app_yml +
                    ':'+current_hash])


def push_docker_image(name_from_app_yml, args_docker_hub_name):
    '''
    This function is to push the docker image once it has been built and
    tagged with the name, and the commit hash tag, which is dependent on the
    functions build_DockerImage and tag_DockerImage functions.
    '''
    print("Pushing the docker image %s" % name_from_app_yml)

    subprocess.call(["docker", "push", args_docker_hub_name +
                    '/'+name_from_app_yml])


if __name__ == '__main__':
    main()
