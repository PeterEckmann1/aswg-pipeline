FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3.8
RUN apt-get -y install python3-pip
RUN apt-get -y install libfontconfig
RUN apt-get -y install poppler-utils
RUN python3.8 -m pip install requests
RUN python3.8 -m pip install beautifulsoup4
RUN python3.8 -m pip install numpy
RUN python3.8 -m pip install fasttext
RUN python3.8 -m pip install spacy
WORKDIR home
COPY src .
CMD python3.8 -u extract.py