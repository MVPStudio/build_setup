FROM ubuntu 
# getting base image ubuntu and if you do not want to create a base image you can say FROM scratch 
MAINTAINER alyssa kelley <abkelley97@gmail.com>
RUN apt-get update
CMD ["echo", "Hello world... this is coming from my first DockerImage!"]
# this would print that to the terminal
