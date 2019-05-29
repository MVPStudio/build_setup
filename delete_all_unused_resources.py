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

    base_path = os.path.abspath(os.path.dirname(__file__))
    working_dir_path = os.path.join(base_path, ".working_tmp")

    deletion_script = "delete_unused_resources.py"

    list_of_unactive = find_unactive_namespaces.find_all_unactive_namespaces()

    go_through_and_delete(deletion_script, args.docker_u,
                          args.docker_p, list_of_unactive,
                          working_dir_path)

    print("Done deleting all of the unused resources.")


def go_through_and_delete(deletion_script, docker_u,
                          docker_p, list_of_unactive,
                          working_dir_path):
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
        delete_unused_resources.delete_all(team_name, docker_u,
                                           docker_p, working_dir_path)


if __name__ == '__main__':
    main()
