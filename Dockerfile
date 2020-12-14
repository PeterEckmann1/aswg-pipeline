FROM ubuntu:20.04
RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get -y install \
        python3.8 \
        openjdk-14-jre \
        python3-pip \
        poppler-utils \
        r-cran-littler \
        libcurl4-gnutls-dev \
        libxml2-dev \
        libssl-dev \
        libgit2-dev \
    && ln -s $(which python3.8) /usr/bin/python
RUN python3.8 -m pip install --upgrade pip \
    && python3.8 -m pip install --no-cache-dir \
        psycopg2-binary \
        requests \
        beautifulsoup4 \
        requests-oauthlib \
        fasttext \
        spacy \
        Pillow \
        pandas \
        scikit-learn==0.22 \
        scikit-image \
        colorspacious \
        fastai==1.0.61 \
        unidecode \
        fastapi \
        uvicorn
RUN Rscript \
    -e 'install.packages("devtools")' \
    -e 'install.packages("tidyverse")' \
    -e 'devtools::install_github("quest-bih/oddpub")'
COPY . .
CMD python3.8 -u server.py