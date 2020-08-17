FROM ubuntu:20.04
RUN apt-get update
RUN apt-get -y install python3.8
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install r-cran-littler
RUN apt-get -y install libcurl4-gnutls-dev libxml2-dev libssl-dev
COPY install.R .
RUN Rscript install.R
WORKDIR home
COPY src .
CMD python3.8 generate_annotation.py