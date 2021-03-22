FROM ubuntu:18.04 as builder
ENV LANG C.UTF-8
RUN apt-get -qq update && apt-get -qqy install git git-lfs
RUN git lfs install
RUN git clone --depth=1 https://github.com/julius-speech/dictation-kit.git
ARG DICTATION_KIT_VERSION=1ceb4dec245ef482918ca33c55c71d383dce145e
RUN cd dictation-kit && git checkout $DICTATION_KIT_VERSION
COPY patch-*.diff /
RUN cd dictation-kit && ls /patch-*.diff | while read file; do \
  patch -p1 < $file; \
done
RUN rm -rf /dictation-kit/.git

FROM julius-base:latest
COPY --from=builder /dictation-kit/bin/common/*.py /decode_engine/scripts/
COPY --from=builder /dictation-kit/*conf /decode_engine/
COPY --from=builder /dictation-kit/model /decode_engine/model
COPY entrypoint.sh parse_output.py /decode_engine/scripts/
RUN chmod +x /decode_engine/scripts/entrypoint.sh
WORKDIR /decode_engine
ENTRYPOINT /decode_engine/scripts/entrypoint.sh
