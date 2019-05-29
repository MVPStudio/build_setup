import yaml
import sys
import os
import subprocess
from subprocess import Popen, PIPE
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
from fabric.api import settings, run


def main():
    base_path = os.path.abspath(os.path.dirname(__file__))
    working_dir_path = os.path.join(base_path, ".working_tmp")

    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'delete_unused_resoures.py '
                                     '--team_name <Team> '
                                     '--docker_u <Username> '
                                     '--docker_p <Password>')

    parser.add_argument('--team_name', type=str, required=False,
                        help='Team name')

    parser.add_argument('--docker_u', type=str, required=True,
                        help='Docker Username')

    parser.add_argument('--docker_p', type=str, required=True,
                        help='Docker Password')

    args = parser.parse_args()
    team_name = args.team_name.replace(" ", "-").replace("_", "-").lower()
    delete_all(team_name, args.docker_u, args.docker_p, working_dir_path)


def delete_all(team_name, docker_user, docker_pass, working_dir_path):

    namespace_filename = team_name + "-namespace.yml"
    quota_filename = team_name + "-quota.yml"
    role_filename = team_name + "-role.yml"
    rolebinding_filename = team_name + "-rolebinding.yml"
    gcloud_serviceaccount_filename = (team_name +
                                      "_gcloud_serviceaccount_key.json")

    namespace_path = os.path.join(working_dir_path, namespace_filename)
    quota_path = os.path.join(working_dir_path, quota_filename)
    role_path = os.path.join(working_dir_path, role_filename)
    rolebinding_path = os.path.join(working_dir_path, rolebinding_filename)
    json_path = os.path.join(working_dir_path, gcloud_serviceaccount_filename)

    delete_team_files(team_name, namespace_path, quota_path,
                      role_path, rolebinding_path)
    delete_kubernetes_namespace(team_name)
    delete_gcloud_serviceaccount(team_name, json_path)
    delete_dockerhub_repo(team_name, docker_user, docker_pass)


def delete_team_files(team_name, namespace_path,
                      quota_path, role_path, rolebinding_path):
    """
    Goes into the .working_tmp directory and deletes the files for the
    team that were used to configure their gcloud and kubernetes
    environments. The files that are being deleted in this function
    are each team's namespace, quota, rile, and rolebinding yml files.
    The helper function delete_file_check confirms the file
    exists in order to delete it, and provides print statements
    of the deletion status.
    """
    delete_file_check(namespace_path)
    delete_file_check(quota_path)
    delete_file_check(role_path)
    delete_file_check(rolebinding_path)

    print("Done deleting files for {}.".format(team_name))


def delete_file_check(file_path):
    """
    Helper function for delete_team_files to check the file exists.
    """
    if os.path.isfile(file_path):
        os.remove(file_path)
        print("{} has been deleted from this directory.".format(file_path))
    else:
        print("Could not find {}.".format(file_path))


def delete_kubernetes_namespace(team_name):
    """
    This function deletes the Kubernetes namespace for this specific team.
    """
    deletion_success = subprocess.call(["kubectl", "delete",
                                        "namespaces", team_name])

    if (deletion_success == 0):
        print("The kubernetes namespace for {} has "
              "been deleted.".format(team_name))

    else:
        print("Unable to delete the kubernetes namepsace "
              "for {}.".format(team_name))


def delete_gcloud_serviceaccount(team_name, gcloud_serviceaccount_json_path):
    """
    This function deletes the gcloud servie account for the team within the
    MVPStudio project, and deletes the json file with the service account's
    information from the .working_temp directory. The service account
    deletion command will prompt the user to confirm it's deletion before
    continuing.
    """
    project_id = "mvpstudio"
    service_account_email = (team_name + '@' + project_id +
                             '.iam.gserviceaccount.com')

    if os.path.isfile(gcloud_serviceaccount_json_path):
        os.remove(gcloud_serviceaccount_json_path)
        print("The gcloud service account json file for {} has been "
              "deleted from the .workingtmp directory.".format(team_name))
    else:
        print("There is no gcloud service account json file for {} in "
              "this directory.".format(team_name))

    delete_service_account_success = subprocess.call(['gcloud', 'iam',
                                                      'service-accounts',
                                                      'delete',
                                                      service_account_email])
    if (delete_service_account_success == 0):
        print("The gcloud service account for {} has been "
              "deleted.".format(team_name))
    else:
        print("There was an error deleting the service account for {},"
              " please do so manually.".format(team_name))


def delete_dockerhub_repo(team_name, docker_username, docker_password):
    """
    This function deletes the team's DockerHub repository within the
    MVPStudio organization.
    """
    login_URL = "https://hub.docker.com/v2/users/login/"
    login_response = requests.post(url=login_URL,
                                   data={"username": docker_username,
                                         "password": docker_password})

    token = login_response.json()['token']
    headers_dict = {"Authorization": "JWT "+token}

    namespace = "mvpstudio"
    reponame = team_name

    repo_URL = ("https://cloud.docker.com/v2/repositories/" +
                namespace+"/"+team_name+"/")

    repo_response = requests.delete(url=repo_URL, headers=headers_dict)

    if (repo_response.status_code == 202):
        print("The DockerHub repository for {} has been "
              "deleted.".format(team_name))
    else:
        print("There was an error deleting the DockerHub repository for {},"
              " please do so manually.".format(team_name))


if __name__ == '__main__':
    main()
