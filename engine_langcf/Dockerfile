FROM engine_langcf_base:latest as builder

FROM python:2.7-stretch
ENV LANG C.UTF-8
COPY --from=builder /crnn-lid/keras /langcf/
COPY model /langcf/model/
RUN apt-get update -qq && apt-get install -qqy sox libsox-fmt-mp3
RUN pip install --no-cache-dir -r /langcf/requirements.txt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT /entrypoint.sh
