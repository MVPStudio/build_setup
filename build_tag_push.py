# Name: Alyssa Kelley
# Last worked on: Jan. 9, 2019

import yaml # Parse the add.yml file
import sys # Potentially use argv[1] for the GitHub URL we are accessing the add.yml file from...
import subprocess

# Step 1 - Read the app.yml file = COMPLETE.
def parseAddFile(filename):
	"""This is using the yaml built in to parse the file automatically with the file name that is opened. Loading info from a yaml file."""
	with open(filename, "r") as file_contents:
		dict_of_contents = yaml.load(file_contents) # might be sys.argv[1] with the GitHub URL to the yml file as the argument when running the python scrip
	name = dict_of_contents['name']
	#print name
	build_script = dict_of_contents['build']
	#print build_script
	test_call = dict_of_contents['test']
	#print test_call
	docker_context_build = dict_of_contents['docker_context'][0]
	#print docker_context_build
	docker_context_static = dict_of_contents['docker_context'][1]
	#print docker_context_static
	return name, build_script, test_call, docker_context_build, docker_context_static # Returns a list of the values from the dictionary dict_of_contents

# Step 2 - Builds and test the app according to that config file = NOT COMPLETE.
# Is this something other than working with Travis CI or is this part of the next step? I was under the impression that 
# Travis CI is what we are using to build and test their app. If not, can you elaborate more on what you want this step to be?

# There needs to be a Build File .travis.yml on their github
# The GitHub repo needs to be added to the Travis CI account and then when there is a new push it will
# run the tests in the .travis.yml file that is in that repo. Ask for clarification...


# Step 3 - Runs docker build with the right context = PARTIALLY COMPLETE.
# They will have their own Dockerfile in their GitHub repo which will then be placed in our MVP Studio dir
# Recall: Dockerfile -> docker build -> Docker Image, it is basically an automation of Docker Image Creation. 
# In the DockerFile, you generally do: FROM = tells Docker which image you base your image on, 
# RUN = tells Docker which additional commands to execute, CMD = tells Docker to execute the command when the image loads.
# You then need to build the Dockerfile to create the image and run image (this is the ID not the name) to create the container

def build_DockerImageandTag(filename):
	""" Sources:
	https://docs.docker.com/compose/gettingstarted/#step-3-define-services-in-a-compose-file
	https://docs.docker.com/engine/reference/commandline/commit/
	https://runnable.com/docker/python/dockerize-your-python-application
	https://www.youtube.com/watch?v=LQjaJINkQXY
	"""
	image_name = parseAddFile(filename)[0] # Name from app.yml file
	subprocess.check_call(["docker", "build", image_name, "."]) # Terminal command: docker build -t $IMAGE_NAME .
	# This . means that you are in the current directory holding the Dockerfile that you need.
	image_id = subprocess.check_call(["docker", "images", "-q", image_name]) # Error here: This ID is still being saved as an int... I will be working on fixing this.
	subprocess.check_call(["docker", "run", image_id])

	##########################################
	# NOT FINISHED HERE -- WILL PICK UP ON IT.
	# Left off on trying to store the Image ID 
	# as an environment variable to use that when 
	# running the ID. 
	##########################################


# Step 4 - Tags the image with the current commit hash & pushed to Docker Hub = NOT COMPLETE.

# Function to find version number and increment this by one and tag the Docker container.
#	Make sure that we have some leading 0's before hard for clarity of version organization.

# Function to find the current hash with revparse check_call.

# Need to conduct a rest request. Using the HTTP package with a request to Docker Hub. (pip install request).

if __name__ == '__main__':
	#filename = "test.yaml"
	filename = "ymltest.yml"
	data = parseAddFile(filename)
	# print data # This will print the returned yaml file information in the form of a list
	build_DockerImageandTag(filename)