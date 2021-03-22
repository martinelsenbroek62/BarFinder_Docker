ARG BASEIMAGE=ubuntu:16.04
FROM $BASEIMAGE
ENV LANG C.UTF-8
RUN apt-get update -qq && apt-get install -qqy curl unzip sox libsox-fmt-mp3 ffmpeg python python-dev patch
ARG CRNN_LID_VERSION=d68538
RUN curl -sSL https://github.com/HPI-DeepLearning/crnn-lid/archive/${CRNN_LID_VERSION}.zip -o /crnn-lid.zip && \
    cd / && unzip crnn-lid.zip && \
    rm -rf /crnn-lid.zip && \
    mv /crnn-lid-${CRNN_LID_VERSION}* /crnn-lid
COPY patch*.diff /
RUN cd /crnn-lid && \
    ls /patch*.diff | while read patch; do patch -p1 < $patch; done
RUN curl https://bootstrap.pypa.io/get-pip.py | python -
RUN pip install --no-cache-dir -r /crnn-lid/keras/requirements.txt
RUN curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
RUN chmod a+rx /usr/local/bin/youtube-dl
RUN pip install --no-cache-dir sox pydub

ARG ENABLE_GPU=false
RUN if [ "$ENABLE_GPU" = "true" ]; then \
  pip install --no-cache-dir tensorflow-gpu==0.12.1 && \
  ln -s libcudnn.so.5.1.10 /usr/lib/x86_64-linux-gnu/libcudnn.so; \
fi
# ENV LD_LIBRARY_PATH=/usr/local/cuda-8.0/targets/x86_64-linux/lib/:$LD_LIBRARY_PATH
