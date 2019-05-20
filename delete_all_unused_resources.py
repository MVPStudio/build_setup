import sys
import os
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description='Usage: python3 '
                                     'delete_all_unused_resoures.py '
                                     '--docker_U <Username '
                                     '--docker_P <Password')

    parser.add_argument('--docker_U', type=str, required=True,
                        help='Docker Username')

    parser.add_argument('--docker_P', type=str, required=True,
                        help='Docker Password')

    args = parser.parse_args()

    namespaces_file = "unactive_namespaces.txt"
    deletion_script = "delete_unused_resources.py"
    find_all_script = "find_unactive_namespaces.py"

    create_unused_file(find_all_script)
    go_through_and_delete(namespaces_file, deletion_script,
                          args.docker_U, args.docker_P)
    os.remove(namespaces_file)

    print("Done deleting all of the unused resources.")


def create_unused_file(find_all_script):
    """
    This function runs the find_unactive_namespaces.py script to
    create a file names unactive_namespaces.txt which contains the
    unactive namespaces.
    """
    print("Running {} to determine all of the unused "
          "namespaces.".format(find_all_script))
    subprocess.call(["python3", find_all_script])


def go_through_and_delete(namespaces_file, deletion_script,
                          docker_U, docker_P):
    """
    This function used the file that was created via the create_unused_file
    function, and loops though those namespaces and individually calls
    the delete_usused_resources.py script to delete each team's
    resources individually.
    """
    print("Going through each unused namespace and running {} to delete"
          " their unused resources.".format(deletion_script))

    with open(namespaces_file, 'r') as file:
        for line in file:
            l = line.strip().split()
            subprocess.call(["python3", deletion_script, "--team_name", l[0],
                             "--docker_U", docker_U, "--docker_P", docker_P])
    file.close()

if __name__ == '__main__':
    main()
