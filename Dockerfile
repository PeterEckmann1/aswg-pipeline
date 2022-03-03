FROM ubuntu:20.04
RUN apt-get update \
    && DEBIAN_FRONTEND="noninteractive" apt-get -y install \
        python3.8 \
        openjdk-17-jre \
        python3-pip \
        poppler-utils \
        r-cran-littler \
        libcurl4-gnutls-dev \
        libxml2-dev \
        libssl-dev \
        libgit2-dev \
        curl \
    && ln -s $(which python3.8) /usr/bin/python
RUN python3.8 -m pip install --upgrade pip \
    && python3.8 -m pip install --no-cache-dir \
        psycopg2-binary \
        requests \
        beautifulsoup4 \
        requests-oauthlib \
        fasttext \
        spacy==2.2.4 \
        Pillow \
        pandas \
        scikit-learn==0.22 \
        scikit-image \
        colorspacious \
        fastai==2.5.3 \
	importlib_resources \
        unidecode \
        fastapi \
        uvicorn
RUN Rscript \
    -e 'install.packages("devtools")' \
    -e 'install.packages("tidyverse")' \
    -e 'devtools::install_github("quest-bih/oddpub")' \
    -e 'devtools::install_github("serghiou/rtransparent@edb1eb9f4628fe372b9850a893bb70ba6e58f673")'
COPY . .
CMD python3.8 -u update.py
