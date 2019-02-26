import unittest
import new_app_setup
import os
import subprocess
import argparse
from unittest.mock import patch
import io
import sys

base_path = os.path.abspath(os.path.dirname(__file__))

path_to_test_namesapce_yml = os.path.join(base_path,
                                'test_data/kubernetes/test_namespace1.yml')
team_name = 'test1'

filename = 'test1.yml'

class TestNewAppSetup(unittest.TestCase):

    def test_create_kubernetes_namespace_yml(self):
        data_from_yml = new_app_setup.create_kubernetes_namespace_yml(filename, team_name)

        self.assertEqual(data_from_yml['kind'], 'Namespace')
        self.assertEqual(data_from_yml['apiVersion'], 'v1')
        self.assertEqual(data_from_yml['metadata']['name'], 'test1')
        self.assertEqual(data_from_yml['metadata']['labels']['name'],
        	             'Hack_For_A_Cause_2019')

if __name__ == '__main__':
	# use minikube on local machine
    unittest.main()
