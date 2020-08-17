FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip
RUN apt-get -y install libfontconfig
RUN apt-get -y install poppler-utils
RUN python3.8 -m pip install numpy
RUN python3.8 -m pip install pandas
RUN python3.8 -m pip install scikit-learn
RUN python3.8 -m pip install scikit-image
RUN python3.8 -m pip install colorspacious
RUN python3.8 -m pip install matplotlib
WORKDIR home
COPY src .
CMD python3.8 -u generate_annotation.py