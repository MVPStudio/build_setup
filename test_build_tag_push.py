import unittest
import build_tag_push
import os
import subprocess
import argparse
from unittest.mock import patch
import io
import sys

base_path = os.path.abspath(os.path.dirname(__file__))

path_to_test_yml = os.path.join(base_path,
                                'test_data/builds_succeeds_example/app.yml')

path_to_fail_test_yml = os.path.join(base_path,
                                     'test_data/build_fails_example/app.yml')


class TestBuildTagPush(unittest.TestCase):

    def test_parse_app_file(self):

        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)
        self.assertEqual(data_from_app_yml['name'], 'build-setup-test')
        self.assertEqual(data_from_app_yml['build'], 'build.sh')
        self.assertEqual(data_from_app_yml['test'], 'test.sh')
        self.assertEqual(data_from_app_yml['docker_context'],
                         ['build', 'static', 'Dockerfile'])

    def test_build_check_app_throws_on_build(self):
        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)

        with self.assertRaises(
             build_tag_push.BuildFailedException) as shouldThrow:

            build_tag_push.build_check_app(data_from_app_yml,
                                           path_to_fail_test_yml, True)

        self.assertEqual("The build failed.", shouldThrow.exception.message)

    def test_build_check_app_runs_build(self):

        build_created_path = os.path.join(base_path, 'test_data/'
                                          'builds_succeeds_example/'
                                          'tmp/build_done.sh')

        # Delete the file if already exists so test this function is creating
        # the file each time it is called.
        if os.path.exists(build_created_path):
            os.remove(build_created_path)

        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)
        build_tag_push.build_check_app(data_from_app_yml, path_to_test_yml,
                                       True)
        self.assertTrue(os.path.exists(build_created_path))

    def test_create_context_directory(self):

        context_array = ['build', 'static', 'Dockerfile']
        test_path = build_tag_push.create_context_directory(context_array,
                                                            path_to_test_yml)
        output = os.listdir(test_path)
        self.assertEqual(output, ['Dockerfile', 'static', 'build'])

    def test_build_docker_image(self):

        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)

        image_name = data_from_app_yml['name']

        subprocess.call(["docker", "rmi", image_name])

        build_tag_push.build_docker_image(data_from_app_yml, path_to_test_yml)

        does_image_exist = subprocess.call(['docker', 'inspect', image_name])

        self.assertEqual(does_image_exist, 0)

    def test_tag_docker_image(self):
        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)

        image_name = data_from_app_yml['name']
        docker_hub_name = 'alyssakelley'

        subprocess.call(["docker", "rmi", image_name])

        build_tag_push.build_docker_image(data_from_app_yml, path_to_test_yml)
        build_tag_push.tag_docker_image(image_name, docker_hub_name)

        test_current_hash = subprocess.check_output(
                            ["git", "log", "-1", "--pretty=%h"]).strip(
                                ).decode('ascii')
        is_imaged_tagged = subprocess.call(['docker', 'image',
                                           'inspect', docker_hub_name + '/' +
                                            image_name + ':' +
                                            test_current_hash])

        self.assertEqual(is_imaged_tagged, 0)

if __name__ == '__main__':
    unittest.main()
