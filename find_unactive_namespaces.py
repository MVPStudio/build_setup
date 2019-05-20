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
    list_of_unactive = []
    find_all_unactive_namespaces(list_of_unactive)
    if len(list_of_unactive) > 0:
        print(list_of_unactive)
        write_unactive_list_to_file(list_of_unactive)

    else:
        print("There are no unactive namespaces found.")


def find_all_unactive_namespaces(list_of_unactive):
    """
    This function uses the kubectl commands to get all of the
    namespaces, and then saves this output to a temp file
    called namespaces.txt which is manually deleted at the
    end of this function. This namespaces.txt file is
    looped through line by line and checks to see if each
    namespace has any pods running, and if it does, then
    this namespace is not added to our list, but if no
    resources are being used, then the namespace is added
    to the unactive list.
    """
    namespaces_file = "namespaces.txt"

    os.system("kubectl get namespace > "+namespaces_file)

    with open(namespaces_file, 'r') as file:
        header = file.readline()
        for line in file:
            l = line.strip().split()

            os.system("kubectl get pods --namespace=" + l[0] +
                      " > temp_output.txt")

            with open("temp_output.txt", 'r') as temp:
                if os.stat("temp_output.txt").st_size == 0:
                    list_of_unactive.append(l[0])
                else:
                    print("Active namespace for {}.".format(l[0]))
                    temp.close()
                    os.remove("temp_output.txt")

    file.close()
    os.remove(namespaces_file)


def write_unactive_list_to_file(list_of_unactive):
    """
    The unactive list is looped through and the namespace names
    are written to a file to later be accessed, specifically
    with the delete_all_unused_resources.py script.
    """
    filename = "unactive_namespaces.txt"

    with open(filename, "w+") as file:
        for team_name in list_of_unactive:
            file.write(team_name+"\n")

    file.close()
    print("The unactive namespaces were saved in the file named "+filename)


if __name__ == '__main__':
    main()
