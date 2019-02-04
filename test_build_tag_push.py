import unittest
import build_tag_push
import os
import subprocess
import argparse
from unittest.mock import patch
import io
import sys

path_to_test_yml = ('/Users/alyssakelley/Desktop/MVPStudio/build_tag_push/'
                    'test_data/builds_succeeds_example/app.yml')

path_to_fail_test_yml = ('/Users/alyssakelley/Desktop/MVPStudio/'
                         'build_tag_push/test_data/build_fails_example/'
                         'app.yml')


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
        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)
        build_tag_push.build_check_app(data_from_app_yml, path_to_test_yml,
                                       True)
        self.assertTrue(os.path.exists('/Users/alyssakelley/Desktop/MVPStudio/'
                        'build_tag_push/test_data/builds_succeeds_example/tmp/'
                                       'build_done.sh'))

    def test_create_context_directory(self):

        context_array = ['build', 'static', 'Dockerfile']
        test_path = build_tag_push.create_context_directory(context_array,
                                                            path_to_test_yml)
        output = os.listdir(test_path)
        self.assertEqual(output, ['Dockerfile', 'static', 'build'])

    def test_build_docker_image(self):
        data_from_app_yml = build_tag_push.parse_app_file(path_to_test_yml)

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        build_tag_push.build_docker_image(data_from_app_yml, path_to_test_yml)
        sys.stdout = sys.__stdout__

        self.assertEqual(capturedOutput.getvalue(), 'Building the docker '
                         'image for build-setup-test\nCreating a '
                         'temporary directory containting [\'build\', '
                         '\'static\', \'Dockerfile\']\n')

    def test_tag_docker_image(self):
        name_from_app_yml = 'build-setup-test'
        docker_hub_name = 'alyssakelley'

        test_current_hash = subprocess.check_output(
                            ["git", "log", "-1", "--pretty=%h"]).strip(
                                ).decode('ascii')

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        build_tag_push.tag_docker_image(name_from_app_yml, docker_hub_name)
        sys.stdout = sys.__stdout__

        self.assertEqual(capturedOutput.getvalue(), "Tagging the docker "
                         "image with the current hash " + test_current_hash +
                         "\n")

    def test_push_docker_image(self):
        name_from_app_yml = 'build-setup-test'
        docker_hub_name = 'alyssakelley'

        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        build_tag_push.push_docker_image(name_from_app_yml, docker_hub_name)
        sys.stdout = sys.__stdout__

        self.assertEqual(capturedOutput.getvalue(), "Pushing the docker image "
                         "build-setup-test\n")

if __name__ == '__main__':
    unittest.main()
