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
                                          'test_data/kubernetes/test1_'
                                          'namespace.yml')

path_to_test_resourcequota_yml = os.path.join(base_path,
                                              'test_data/kubernetes/test1_'
                                              'quota.yml')

path_to_test_config_yml = os.path.join(base_path, 'test_data/kubernetes/'
                                       'test1_config_file.yml')

path_to_test_access_token_txt = os.path.join(base_path, 'test_data/kubernetes/'
                                             'access_token_from_config_'
                                             'test1.txt')

team_name = 'test1'
RAM = "2"
CPU = "1"


class TestNewAppSetup(unittest.TestCase):

    def test_create_kubernetes_namespace_yml(self):
        data_from_yml = new_app_setup.create_namespace_yml(
            path_to_test_namesapce_yml, team_name)

        self.assertEqual(data_from_yml['kind'], 'Namespace')
        self.assertEqual(data_from_yml['apiVersion'], 'v1')
        self.assertEqual(data_from_yml['metadata']['name'], 'test1')
        self.assertEqual(data_from_yml['metadata']['labels']['name'],
                         'Hack_For_A_Cause_2019')

    def test_create_kubernetes_ResourceQuota_yml(self):
        data_from_yml = new_app_setup.create_ResourceQuota(
            path_to_test_resourcequota_yml, team_name, RAM, CPU)

        self.assertEqual(data_from_yml['apiVersion'], 'v1')
        self.assertEqual(data_from_yml['kind'], 'ResourceQuota')
        self.assertEqual(data_from_yml['metadata']['name'], 'test1')
        self.assertEqual(data_from_yml['spec']['hard']['requests.cpu'],
                         CPU)
        self.assertEqual(data_from_yml['spec']['hard']['limits.cpu'],
                         "1")
        self.assertEqual(data_from_yml['spec']['hard']['requests.memory'],
                         RAM+"G")
        self.assertEqual(data_from_yml['spec']['hard']['limits.memory'],
                         "2G")

    def test_create_config_yml(self):
        new_app_setup.get_congif_yml_file(team_name)

        exists = os.path.isfile(path_to_test_config_yml)

        self.assertTrue(exists)

    def test_get_access_token(self):
        new_app_setup.get_access_token(path_to_test_config_yml, team_name)

        exists = os.path.isfile(path_to_test_access_token_txt)

        self.assertTrue(exists)


if __name__ == '__main__':
    unittest.main()
