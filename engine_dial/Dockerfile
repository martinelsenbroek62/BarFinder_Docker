ARG BASEIMAGE=local-deep-speech:latest-gpu
FROM local-deep-speech:latest-cpu AS builder
ADD decoder/* /DecodeEngine/
RUN cd /DecodeEngine && make decode

FROM $BASEIMAGE
COPY --from=builder /DecodeEngine/decode /DecodeEngine
# COPY --from=builder /DecodeEngine/decode.py /DecodeEngine
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT /entrypoint.sh
