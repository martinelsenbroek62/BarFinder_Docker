FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04

ENV SHELL /bin/bash

RUN apt-get update -qq && apt-get install -y git unzip bzip2 wget vim sox g++ make python python3 python-pip python3-pip zlib1g-dev automake autoconf libtool subversion libatlas-base-dev

RUN git clone --depth 1 https://github.com/kaldi-asr/kaldi.git kaldi

RUN cd /kaldi/tools && make -j 10
RUN cd /kaldi/src && ./configure --shared --mathlib=ATLAS && make depend -j 10 && make -j 10
