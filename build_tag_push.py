# Name: Alyssa Kelley
# Last worked on: Jan. 14, 2019

import yaml # Parse the add.yml file
import sys 
import os
import subprocess
from shutil import copyfile # Allowing me to copy dockerfile context to new temp dir

Docker_Hub_Name = "alyssakelley" # This is my personal docker namespace/username for testing.
# If we want to make this a user input option --> Docker_Hub_Name = input('Enter your Docker namespace: ')

# Step 1 - Read the app.yml file = COMPLETE.

def parseAppFile(filename):
	''' 
	This function is using the yaml built in to parse the file which can be done by searching for 
	the key in the dictionary for the yaml file. 

	Example: name = dict_of_contents['name']
	'''
	with open(filename, "r") as file_contents:
		dict_of_contents = yaml.load(file_contents) # might be sys.argv[1] with the GitHub URL to the yml file as the argument when running the python scrip
	# name = dict_of_contents['name']
	# build_script = dict_of_contents['build']
	# test_call = dict_of_contents['test']
	# docker_context_build = dict_of_contents['docker_context'][0]
	# docker_context_static = dict_of_contents['docker_context'][1]
	return dict_of_contents

# Step 2 - Builds and test the app according to that config file = PENDING.

# Is this something other than working with Travis CI or is this part of the next step? 
# I was under the impression that Travis CI is what we are using to build and test their app. 
# If not, can you elaborate more on what you want this step to be?

def createContextDirectory(contextArray):
	original_dir_path = os.getcwd() # Getting this path to copy over files later in this function. I am assuming
									# this is where the original files were put that we will be working out of.

	dir_name = "MVPStudio_temp_dir" 
	# Should this be user input so it can be different names per group? -->
	# dir_name = input('Enter a directory name for your Docker Context: ')

	os.makedirs(dir_name, exist_ok=True) # Making the directory and saying to not raise an error if the directory already exists.

	dir_path = original_dir_path+'/'+dir_name # This is providing the path to the Docker Context directory.

	copyfile(original_dir_path+'/'+contextArray[0], dir_path+'/'+contextArray[0]) # Copying the first file from docker_context
																				  # and putting it in the Docker Context directory 
																				  # created.
	copyfile(original_dir_path+'/'+contextArray[1], dir_path+'/'+contextArray[1]) # Copying the first file from docker_context

	return dir_path

# Step 3 - Runs docker build with the right context =  COMPLETE.

# Notes on Docker (for myself as I am working):

# They will have their own Dockerfile in their GitHub repo which will then be placed in our MVP Studio dir
# Recall: Dockerfile -> docker build -> Docker Image, it is basically an automation of Docker Image Creation. 
# In the DockerFile, you generally do: FROM = tells Docker which image you base your image on, 
# RUN = tells Docker which additional commands to execute, CMD = tells Docker to execute the command when the image loads.

def build_DockerImage(filename):
	docker_dir_context = createContextDirectory(parseAppFile(filename)['docker_context']) # This will be the build and static file (and needs a Dockerfile as well)
	image_name = parseAppFile(filename)['name'] # Name from app.yml file
	subprocess.check_call(["docker", "build", docker_dir_context, "-t", image_name]) # this builds the docker image.

	# QUESTION: When I try to build the image from the file that has the docker context from the app.yml file 
	# then I get the error: "Build an image from a Dockerfile". The only way I was able to complete this was 
	# putting in my own Dockerfile, which I am assuming the groups will have as well and we will need to copy
	# this over into that directory created, or is this going to be copied over manually?

# Step 4 - Tags the image with the current commit hash & push to Docker Hub = COMPLETE.

def tag_DockerImage(filename):
	'''
	This function is finding the tagging the Docker Image with the name of the user/image_name, and the current git hash. 
	Note: The current git hash is shortened a bit, but to display the full hash, then change the lower case %h to upper case %H. 
	The source for this command is: https://container-solutions.com/tagging-docker-images-the-right-way
	'''
	image_name = parseAppFile(filename)['name']

	subprocess.check_call(["docker", "tag", image_name, Docker_Hub_Name+'/'+image_name]) # Need to tag the image with the namespace for the Docker Hub account. 
																						 # Note: I made this a global variable for now with a comment for user input if needed.

	current_hash = str(subprocess.check_call(["git", "log", "-1", "--pretty=%h"])) # Note: having the lower case 'h' provides a shorter version of the hash... 
	 																			   # I read that the shorter tag was better so I did that here.

	subprocess.check_call(["docker", "tag", image_name, Docker_Hub_Name+'/'+image_name+':'+current_hash]) # This tags the image with the current hash.

	# QUESTION: When I am running this function, the current_hash is turning to the number 0, and not what the actual current_hash is when observed in the terminal (which is 07f21e2), 
	# I have been having this problem a lot with setting a variable = terminal command... it always becomes 0. Is there something I am doing wrong or missing with this?

def push_DockerImage(filename):
	'''
	This function is to push the docker image once it has been built and tagged with the name, and the commit hash tag, which is dependent on the 
	functions build_DockerImage and tag_DockerImage functions.
	'''
	image_name = parseAppFile(filename)['name']
	subprocess.check_call(["docker", "push", Docker_Hub_Name+'/'+image_name])

if __name__ == '__main__':
	#filename = "test.yaml"
	filename = "ymltest.yml"
	data_from_appyaml = parseAppFile(filename)
	createContextDirectory(parseAppFile(filename)['docker_context'])
	#print(parseAppFile(filename)['docker_context'])
	build_DockerImage(filename)
	tag_DockerImage(filename)
	push_DockerImage(filename)

# Comments regarding testing: 
# I have not created unit tests for this yet, I am just testing it all manually through test files I have made, and calling 
# it all in main. My next step is to learn about unit tests and implement them. 














