ARG BASEIMAGE=localpaddle:0.15.0-gpu-cuda9.2-cudnn7
FROM $BASEIMAGE
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/lib
COPY *.whl /_compile/
RUN apt-get -qyy update && \
  apt-get -qyy install curl git unzip pkg-config libflac-dev libogg-dev libvorbis-dev libboost-dev swig && \
  curl -sL https://github.com/PaddlePaddle/DeepSpeech/archive/15de13ede159a38db009524077a46211803f4a47.zip -o /deep-speech.zip && \
  cd / && unzip /deep-speech.zip && rm -rf deep-speech.zip && mv DeepSpeech-* DecodeEngine && \
  cd DecodeEngine && sh setup.sh && \
  pip install --no-cache-dir /_compile/*.whl && \
  apt-get purge -qyy curl git unzip pkg-config && \
  apt-get autoremove -y && apt-get clean -y && rm -rf /root/.cache 
COPY ["compile_all", "compile.py", "patch*.diff", "/_compile/"]
RUN bash /_compile/compile_all && rm -rf /root/.cache
WORKDIR /DecodeEngine
