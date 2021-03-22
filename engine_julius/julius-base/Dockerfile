FROM ubuntu:18.04 as builder
ENV LANG C.UTF-8
RUN apt-get -qq update && apt-get -qqy install build-essential zlib1g-dev libsdl2-dev libasound2-dev git
ARG JULIUS_VERSION=v4.5
RUN git clone --depth=1 https://github.com/julius-speech/julius.git --branch $JULIUS_VERSION
RUN cd julius && ./configure --enable-words-int
RUN cd julius && make -j4

FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04 as python-builder
ENV LANG C.UTF-8
RUN apt-get -qq update && apt-get -y install python python-dev curl
RUN curl -sSL https://bootstrap.pypa.io/get-pip.py -o /get-pip.py
RUN python /get-pip.py
RUN pip wheel numpy
ENV NVCCFLAGS "-gencode arch=compute_30,code=sm_30 -gencode arch=compute_32,code=sm_32 -gencode arch=compute_35,code=sm_35 -gencode arch=compute_50,code=sm_50 -gencode arch=compute_52,code=sm_52 -gencode arch=compute_53,code=sm_53 -gencode arch=compute_60,code=sm_60 -gencode arch=compute_61,code=sm_61 -gencode arch=compute_62,code=sm_62 -gencode arch=compute_70,code=sm_70 -gencode arch=compute_72,code=sm_72"
ARG CUDAMAT_VER=6f4dbc773bfd0fa2b1d38939837b9019ac21d26e
RUN pip wheel https://github.com/cudamat/cudamat/archive/${CUDAMAT_VER}.zip

FROM nvidia/cuda:9.2-cudnn7-runtime-ubuntu16.04
RUN apt-get -qq update && apt-get -y install libpulse0 libasound2 libgomp1 python python-dev expect
COPY --from=python-builder /get-pip.py /*.whl /
COPY --from=builder /julius/julius/julius /julius/adintool/adintool /usr/local/bin/
RUN python get-pip.py && rm -rf /get-pip.py && \
    pip install --no-cache-dir /*.whl
