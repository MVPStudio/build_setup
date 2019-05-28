import sys
import os
import subprocess
import argparse
import delete_unused_resources
import find_unactive_namespaces


def main():
    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'delete_all_unused_resoures.py '
                                     '--docker_u <Username '
                                     '--docker_p <Password')

    parser.add_argument('--docker_u', type=str, required=True,
                        help='Docker Username')

    parser.add_argument('--docker_p', type=str, required=True,
                        help='Docker Password')

    args = parser.parse_args()

    deletion_script = "delete_unused_resources.py"

    list_of_unactive = find_unactive_namespaces.find_all_unactive_namespaces()

    go_through_and_delete(namespaces_file, deletion_script,
                          args.docker_u, args.docker_p, list_of_unactive)

    print("Done deleting all of the unused resources.")


def go_through_and_delete(namespaces_file, deletion_script,
                          docker_u, docker_p, list_of_unactive):
    """
    This function uses the unactive list of namespaces,
    and loops though those namespaces and individually calls
    the delete_usused_resources.py functions to delete each team's
    resources individually.
    """
    print("Going through each unused namespace and running {} to delete"
          " their unused resources.".format(deletion_script))

    for i in range(len(list_of_unactive)):
        team_name = list_of_unactive[i]

        base_path = os.path.abspath(os.path.dirname(__file__))
        working_dir_path = os.path.join(base_path, ".working_tmp")

        namespace_path = os.path.join(working_dir_path,
                                      (team_name + "-namespace.yml"))
        quota_path = os.path.join(working_dir_path,
                                  (team_name + "-quota.yml"))
        role_path = os.path.join(working_dir_path, (team_name + "-role.yml"))
        rolebinding_path = os.path.join(working_dir_path,
                                        (team_name + "-rolebinding.yml"))
        json_path = os.path.join(working_dir_path, (team_name +
                                                    "_gcloud_service" +
                                                    "account_key.json"))

        delete_unused_resources.delete_team_files(team_name, namespace_path,
                                                  quota_path, role_path,
                                                  rolebinding_path)
        delete_unused_resources.delete_kubernetes_namespace(team_name)
        delete_unused_resources.delete_gcloud_serviceaccount(team_name,
                                                             json_path)
        delete_unused_resources.delete_dockerhub_repo(team_name,
                                                      docker_u, docker_p)


if __name__ == '__main__':
    main()
