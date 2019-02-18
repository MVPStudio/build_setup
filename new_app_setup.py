import yaml
import sys
import os
import subprocess
import shutil
from shutil import copyfile
import argparse
import tempfile
# import github from Github
# import pygit2

# python3 new_app_setup.py test_new_app1


def main():
    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'new_app_setup.py <Team name> '
                                     '<List of users>')

    parser.add_argument('team_name', type=str,
                        help='Team name')

    # parser.add_argument('list_of_users', type=list,
    #                     help='A list of the users for this team.')

    args = parser.parse_args()

    team_name = args.team_name.replace(" ", "_").lower()

    filename = team_name+".yml"

    yml_config_file = create_yml(team_name)

    create_kubernetes_namespace(yml_config_file)


def create_yml(filename, team_name):

    yml_file_kubernetes_data = dict(

        kind='Namespace',
        apiVersion='v1',
        metadata=dict(
            name=team_name,
            # labels = dict(
            # 	name = team_name+'tag',  # Do we need a specific tag?
            # 	)
            )
        )

    with open(filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    return yml_file_kubernetes_data


def create_kubernetes_namespace(filename):
    subprocess.call(['kubectl', 'create', '-f', filename])


def create_bucket():
    pass


def add_users(filename, list_of_users):
    pass
    # for user in list_of_users:


# def create_github_repo(team_name):
# 	g = Github(userName, password)
# 	org = g.get_organization('MVPStudio')
# 	project_description = ("Team " + team_name + " repo for Hack For A Cause")
# 	repo = org.create_repo(team_name, description = project_description)


if __name__ == '__main__':
    main()
