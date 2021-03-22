FROM nvidia/cuda:9.2-cudnn7-runtime-ubuntu16.04
MAINTAINER PaddlePaddle Authors <paddle-dev@baidu.com>
ENV HOME /root
ADD *.whl /
# run paddle version to install python packages first
RUN apt-get update  && \
    apt-get install -y wget python-pip python-opencv libgtk2.0-dev dmidecode python-tk && easy_install -U pip && \
    pip install /*.whl; apt-get install -f -y && \
    apt-get clean -y && \
    rm -f /*.whl && \
    ldconfig
RUN ln -sf /usr/lib/x86_64-linux-gnu/libcudnn.so.7 /usr/lib/x86_64-linux-gnu/libcudnn.so
RUN ln -sf /usr/local/cuda/targets/x86_64-linux/lib/libcublas.so.9.2 /usr/lib/x86_64-linux-gnu/libcublas.so
RUN ln -sf /usr/local/cuda-9.2/targets/x86_64-linux/lib/libcurand.so.9.2 /usr/lib/x86_64-linux-gnu/libcurand.so
ENV LD_LIBRARY_PATH /usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}
ENV NCCL_LAUNCH_MODE PARALLEL
# default command shows the paddle version and exit
CMD ["true"]
