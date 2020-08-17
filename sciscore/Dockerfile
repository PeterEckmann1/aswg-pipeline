FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip
RUN python3.8 -m pip install requests
RUN python3.8 -m pip install scikit-learn==0.22
WORKDIR home
COPY src .
CMD python3.8 -u generate_annotation.py