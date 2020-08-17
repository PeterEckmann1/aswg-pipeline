FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3.8
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install openjdk-14-jre
WORKDIR home
COPY src .
CMD python3.8 generate_annotation.py