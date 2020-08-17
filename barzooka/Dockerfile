FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip
RUN apt-get -y install libfontconfig
RUN apt-get -y install poppler-utils
RUN python3.8 -m pip install requests
RUN python3.8 -m pip install numpy
RUN python3.8 -m pip install fastai
RUN python3.8 -m pip install urllib3
RUN python3.8 -m pip install pandas
WORKDIR home
COPY src .
CMD python3.8 -u generate_annotation.py