import yaml
import sys
import os
import subprocess
import shutil
import array
from shutil import copyfile
import argparse
import tempfile
import smtplib
from google.cloud import storage


def main():

    base_path = os.path.abspath(os.path.dirname(__file__))

    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'new_app_setup.py <Team name> '
                                     '<Group user> '
                                     '<Optional - List of users> '
                                     '<Optional - Requested RAM> '
                                     '<Optional - Requested CPU>')

    parser.add_argument('--team_name', type=str, required=True,
                        help='Team name')

    parser.add_argument('--group_user', type=str, required=True,
                        help='An email address that '
                        'will be used for the entire group as a whole.')

    parser.add_argument('-LOU', '--list_of_users',
                        required=False,
                        help='A list of the users for this team.')

    parser.add_argument('-RAM', '--RAM', type=int, required=False,
                        default=2, help="How many gigabytes of RAM your "
                        "team is requesting, the deault is 2G.")

    parser.add_argument('-CPU', '--CPU', type=int, required=False,
                        default=1, help="How much CPU your team "
                        "is requesting, the default is one.")

    args = parser.parse_args()

    team_name = args.team_name.replace(" ", "-").replace("_", "-").lower()

    namespace_filename = team_name + "_namespace.yml"

    create_namespace_yml(namespace_filename, team_name)

    kube_apply(namespace_filename, team_name, "namespace")

    quota_filename = team_name + "_quota.yml"

    create_ResourceQuota(quota_filename, team_name, args.RAM, args.CPU)

    kube_apply_ResourceQuota(quota_filename, team_name, "ResourceQuota")

    config_file = get_congif_yml_file(team_name)

    get_access_token(config_file, team_name)


def create_namespace_yml(namespace_filename, team_name):

    tag = "Hack_For_A_Cause_2019"

    yml_file_kubernetes_data = dict(

        kind='Namespace',
        apiVersion='v1',
        metadata=dict(
            name=team_name,
            labels=dict(
                name=tag
                )
            )
        )

    with open(namespace_filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    print("The YAML file for {} was created and was "
          "saved as {}".format(team_name, namespace_filename))

    return yml_file_kubernetes_data


def create_ResourceQuota(quota_filename, team_name, RAM, CPU):

    yml_file_kubernetes_data = {

        'apiVersion': 'v1',
        'kind': 'ResourceQuota',
        'metadata':
        {
            'name': team_name,
        },
        'spec':
        {
            'hard':
            {
                'requests.cpu': str(CPU),
                'requests.memory': (str(RAM)+"G"),
                'limits.cpu': "1",
                'limits.memory': "2G"
            }
        }
    }

    with open(quota_filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    print("The ResourceQuota YAML file for {} was created and was "
          "saved as {}".format(team_name, quota_filename))

    return yml_file_kubernetes_data


def kube_apply(filename, team_name, type_of_create):
    subprocess.check_call(['kubectl', 'apply', '-f', filename])

    print("The Kubernetes {} for {} was "
          "created.".format(type_of_create, team_name))


def kube_apply_ResourceQuota(filename, team_name, type_of_create):
    """
    Created a specific function to apply the ResourceQuota to include the
    --namespace flag.
    """
    subprocess.check_call(['kubectl', 'apply', '-f',
                          filename, '--namespace='+team_name])

    print("The Kubernetes {} for {} was "
          "created.".format(type_of_create, team_name))


def get_congif_yml_file(team_name):
    """
    This function is pulling the information from the configuration
    file for the team's namespace and putting it into another file that
    we can later access. This is specifically going to be used for
    retrieving the access-token.
    """
    config_filename = team_name+'_config_file.yml'

    terminal_command = ['kubectl', 'config', 'view']

    with open(config_filename, 'w') as outfile:
        subprocess.check_call(terminal_command, stdout=outfile)

    print("The config file for {} was created and saved as {} in the "
          "current folder".format(team_name, config_filename))

    return config_filename


def get_access_token(config_file, team_name):
    """
    This function is using the configuration file we created with
    get_congif_yml_file and the parsing it to store only the access
    token in a separate file so we can hand that to the Hack-For-A-
    Cause teams. The file name for the tokens would be
    access_token_from_config_<team_name>.txt and is placed in the
    current directory with the other yml files created.
    """
    with open(config_file, "r") as file_contents:
        dict_of_contents = yaml.load(file_contents)

    filename_for_token = "access_token_from_config_"+team_name+".txt"

    access_token = (dict_of_contents['users'][0]['user']['auth-provider']
                    ['config']['access-token'])

    f = open(filename_for_token, "w+")

    f.write(access_token)

    f.close()

    print("The access token for {} has been parsed and placed in "
          "a file named {}".format(team_name, filename_for_token))


def add_users(team_name, group_user):
    pass


def create_role_yml(role_filename, team_name, group_user):
    pass


def create_rolebinding_yml(rolebinding_filename, team_name, group_user):
    pass


if __name__ == '__main__':
    main()
