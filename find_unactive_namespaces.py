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
import tempfile


def main():
    list_of_unactive = find_all_unactive_namespaces()
    if len(list_of_unactive) > 0:
        print(list_of_unactive)

    else:
        print("There are no unactive namespaces found.")


def find_all_unactive_namespaces():
    """
    This function uses the kubectl commands to get all of the
    namespaces, and then saves this output to a tempfile.
    This file is looped through line by line and checks to see if each
    namespace has any pods running, and if it does, then
    this namespace is not added to our list, but if no
    resources are being used, then the namespace is added
    to the unactive list, which is returned.
    """
    all_namespaces = subprocess.check_output(['kubectl', 'get', 'namespaces'],
                                             stderr=subprocess.STDOUT)

    list_of_unactive = []

    tmp = tempfile.TemporaryFile()
    tmp.write(all_namespaces)
    tmp.seek(0)

    header = tmp.readline()
    for line in tmp:
        l = line.decode().strip().split()
        response = subprocess.check_output(['kubectl', 'get', 'pods',
                                            '--namespace=' + l[0]],
                                           encoding="UTF-8",
                                           stderr=subprocess.STDOUT)
        unactive_response = 'No resources found.'

        if response.strip() == unactive_response:
            list_of_unactive.append(l[0])
            print("{} is an unactive namespace.".format(l[0]))
        else:
            print("Active namespace for {}.".format(l[0]))

    return list_of_unactive


if __name__ == '__main__':
    main()
