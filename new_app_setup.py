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
from google.oauth2 import service_account
import googleapiclient.discovery
import requests


def main():
    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'new_app_setup.py <Team name> '
                                     '<Group user> '
                                     '[options]')

    parser.add_argument('--team_name', type=str, required=True,
                        help='Team name')

    parser.add_argument('--docker_U', type=str, required=True,
                        help='Docker Username')

    parser.add_argument('--docker_P', type=str, required=True,
                        help='Docker Password')

    parser.add_argument('-r', '--RAM', type=int, required=False,
                        default=2, help="How many gigabytes of RAM your "
                        "team is requesting, the deault is 2G.")

    parser.add_argument('-c', '--CPU', type=int, required=False,
                        default=1, help="How much CPU your team "
                        "is requesting, the default is one.")

    args = parser.parse_args()

    working_dir = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), '.working_tmp')

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    team_name = args.team_name.replace(" ", "-").replace("_", "-").lower()

    docker_username = args.docker_U
    docker_password = args.docker_P

    create_docker_repo(team_name, docker_username, docker_password)

    namespace_filename = os.path.join(
        working_dir, team_name + "-namespace.yml")

    create_namespace_yml(namespace_filename, team_name)

    kube_create_namespace(namespace_filename, team_name, "namespace")

    quota_filename = os.path.join(working_dir, team_name + "-quota.yml")

    create_resource_quota(quota_filename, team_name, args.RAM, args.CPU)

    kube_apply_resource_quota(quota_filename, team_name, "resource-quota")

    create_gcloud_service_account(team_name, working_dir)

    role_filename = os.path.join(working_dir, team_name + "-role.yml")

    create_role_yml(role_filename, team_name)

    rolebinding_filename = os.path.join(
        working_dir, team_name + "-rolebinding.yml")

    create_rolebinding_yml(rolebinding_filename, team_name)


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


def create_resource_quota(quota_filename, team_name, RAM, CPU):

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
                'requests.memory': (str(RAM) + "G"),
                'limits.cpu': str(CPU),
                'limits.memory': (str(RAM) + "G")
            }
        }
    }

    with open(quota_filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    print("The resource_quota YAML file for {} was created and was "
          "saved as {}".format(team_name, quota_filename))

    return yml_file_kubernetes_data


def kube_create_namespace(filename, team_name, type_of_create):

    subprocess.check_call(['kubectl', 'apply', '-f', filename])

    print("The Kubernetes {} for {} was "
          "created.".format(type_of_create, team_name))


def kube_apply_resource_quota(filename, team_name, type_of_create):
    """
    Created a specific function to apply the resource_quota to include the
    --namespace flag.
    """
    subprocess.check_call(['kubectl', 'apply', '-f',
                           filename, '--namespace=' + team_name])

    print("The Kubernetes {} for {} was "
          "created.".format(type_of_create, team_name))


def create_gcloud_service_account(team_name, working_dir):

    project_id = 'mvpstudio'

    key_filename = os.path.join(
        working_dir, team_name+"_gcloud_serviceaccount_key.json")

    subprocess.check_call(['gcloud', 'iam', 'service-accounts',
                           'create', team_name])

    print("Created the service account: ", team_name)

    service_account_email = (team_name + '@'+project_id +
                             '.iam.gserviceaccount.com')

    subprocess.check_call(['gcloud', 'iam', 'service-accounts',
                           'keys', 'create', key_filename, '--iam-account',
                           service_account_email])

    subprocess.check_call(['gcloud', 'projects', 'add-iam-policy-binding',
                           'mvpstudio', '--member', 'serviceAccount:' +
                           service_account_email, '--role',
                           'projects/mvpstudio/roles/AppTeamServiceAccount'])

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_filename

    print("Generated the key file and saved it as ", key_filename)


def create_role_yml(role_filename, team_name):
    """
    https://kubernetes.io/docs/reference/
    access-authn-authz/rbac/#role-and-clusterrole
    """
    yml_file_kubernetes_data = dict(

        apiVersion='rbac.authorization.k8s.io/v1',
        kind='Role',
        metadata=dict(
            namespace=team_name,
            name=team_name+"-role",
        ),
        rules=[
            {
                'apiGroups': ['*'],
                'resources': [
                    'pods',
                    'pods/*',
                    'deployments',
                    'services',
                    'configmaps',
                    'persistentvolumeclaims',
                    'persistentvolumes',
                    'secrets',
                    'serviceaccounts',
                    'replicasets',
                    'statefulsets',
                    'cronjobs',
                    'jobs'
                ],
                'verbs': ['get', 'watch', 'list', 'create', 'update', 'patch'],
            }
        ],
    )

    with open(role_filename, 'w') as outfile:
        print('YAML IN:', role_filename)
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    subprocess.check_call(['kubectl', 'apply', '-f', role_filename])


def create_rolebinding_yml(rolebinding_filename, team_name):
    """
    Rolebinding allows the team to be able to access their
    specific namespace.
    """
    yml_file_kubernetes_data = dict(

        apiVersion='rbac.authorization.k8s.io/v1',
        kind='RoleBinding',
        metadata=dict(
            name='team-service-account-binding',
            namespace=team_name,
        ),
        subjects=[
            {
                'kind': 'User',
                'name': team_name+'@mvpstudio.iam.gserviceaccount.com',
                'apiGroup': 'rbac.authorization.k8s.io',
            }
        ],
        roleRef={
            'kind': 'Role',
            # this must match the name of the Role it is binding to
            'name': team_name+"-role",  # this should be the name of the Role
            'apiGroup': 'rbac.authorization.k8s.io',
        }
    )

    with open(rolebinding_filename, 'w') as outfile:
        yaml.dump(yml_file_kubernetes_data, outfile, default_flow_style=False)

    subprocess.check_call(['kubectl', 'apply', '-f',
                           rolebinding_filename, '--namespace='+team_name])


def create_docker_repo(team_name, docker_username, docker_password):
    """
    This function logs into DockerHub and keeps track of that token
    to pass in when creating the DockerHub repository for each
    team under the MVPStudio organziation.
    """
    login_URL = "https://hub.docker.com/v2/users/login/"

    login_response = requests.post(url=login_URL, data={"username":
                                   docker_username,
                                   "password": docker_password})

    token = login_response.json()['token']

    data = {"namespace": "mvpstudio",
            "registry": "registry-1.docker.io",
            "image": "mvpstudio/"+team_name,
            "build_in_farm": "true",
            "name": team_name,
            "description": team_name+" Hack for a Cause 2019",
            "privacy": "public",
            "build_settings": [{"nocache": "false",
                                "build_context": "/",
                                "source_type": "Branch",
                                "tag": "latest",
                                "dockerfile": "Dockerfile",
                                "source_name": "master",
                                "autobuild": "true"}],
            "is_private": "false"
            }

    repo_URL = "https://cloud.docker.com/v2/repositories/"

    headers_dict = {"Authorization": "JWT "+token}

    repo_response = requests.post(url=repo_URL,
                                  data=data, headers=headers_dict)

    repo_info = repo_response.text
    print(repo_info)


if __name__ == '__main__':
    main()
