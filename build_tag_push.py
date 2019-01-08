# Name: Alyssa Kelley
# Last worked on: Jan. 8, 2018

import yaml # Parse the add.yml file
import sys # Potentially use argv[1] for the GitHub URL we are accessing the add.yml file from...
import os # Using this to store variables as environment variables and run terminal commands.

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
# There needs to be a Build File .travis.yml on their github
# Seems as though the GitHub repo needs to be added to the Travis CI account and then when there is a new push it will
# run the tests in the .travis.yml file that is in that repo. Ask for clarification...
#
#
#
#
#
#
#
#
#
#

# Step 3 - Runs docker build with the right context = PARTIALLY COMPLETE.
# They will have their own Dockerfile in their GitHub repo (I am assuming) and this file is a text file with 
# instructions to build image. Dockerfile -> docker build -> Docker Image, it is basically an automation of Docker Image
# Creation. In the DockerFile, you generally do: FROM = tells Docker which image you base your image on, 
# RUN = tells Docker which additional commands to execute, CMD = tells Docker to execute the command when the image loads.
# You then need to build the Dockerfile to create the image and run image (this is the ID not the name) to create the container

def build_DockerImageandTag(filename):
	""" Helpful sources:
	https://docs.docker.com/compose/gettingstarted/#step-3-define-services-in-a-compose-file
	https://docs.docker.com/engine/reference/commandline/commit/
	https://runnable.com/docker/python/dockerize-your-python-application
	https://www.youtube.com/watch?v=LQjaJINkQXY
	"""
	os.environ['IMAGE_NAME'] = parseAddFile(filename)[0] # This is creating the environment variable $IMAGE_NAME based
	# off of the add.yml file that is in their GitHub repo and since I am returning their add.yml contents as a list
	# in my parseAddFile function, I am indexing that list to get the name out.
	os.system("echo $IMAGE_NAME") # This is just a check to make sure I am getting the correct result. Success.
	os.system("docker build -t $IMAGE_NAME .") 
	# This . means that you are in the current directory holding the Dockerfile that you need.
	# You can give an exact location instead of the . so for my setup it would be /Users/alyssakelley/Desktop/MVP Studio/DockerFiles
	# You can have the -t flag to tag the image. So it would be: docker build -t imagename:tag . 
	# Note: Then if you want to run that Docker image that was just created, you can do the following command in the terminal:
	# 	docker run <image ID> 
	# Note: The Image ID you can access with the command 'docker images'
	image_id = os.system("docker images -q $IMAGE_NAME")
	print image_id
	#os.environ['IMAGE_ID'] = image_id  # This -q flag retrieves the last image ID (Doesn't work... TypeError)
	#os.system("docker run $IMAGE_ID")
	#os.system("docker run docker images -q $IMAGE_NAME") -> Nope.
	#os.system("docker images -q $IMAGE_NAME")
	#os.system("IMAGE_ID=$(docker images -q $IMAGE_NAME)")
	os.system("echo done")
	#os.system('docker run $IMAGE_ID')

	##########################################
	# NOT FINISHED HERE -- WILL PICK UP ON IT.
	# Left off on trying to store the Image ID 
	# as an environment variable to use that when 
	# running the ID. 
	##########################################


# Step 4 - Tags the image with the current commit hash & pushed to Docker Hub = NOT COMPLETE.
#
#
#
#
#
#
#
#
#
#
#

if __name__ == '__main__':
	#filename = "test.yaml"
	filename = "ymltest.yml"
	data = parseAddFile(filename)
	# print data # This will print the returned yaml file information in the form of a list
	build_DockerImageandTag(filename)