FROM kaldi_base:latest as builder

COPY 0002_cvte_chain_model_v2.tar.gz /kaldi/egs

RUN cd /kaldi/egs && tar xvf 0002_cvte_chain_model_v2.tar.gz

RUN mv /kaldi/egs/cvte/s5 /DecodeModel


FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04

ENV LC_ALL "C"

RUN apt-get update -qq && apt-get install -qqy libatlas3-base python3 python3-docopt

COPY --from=builder /DecodeModel /DecodeModel/
COPY --from=builder /kaldi/src/cudadecoderbin/batched-wav-nnet3-cuda /usr/bin/wav-gpu-decoder
COPY --from=builder /kaldi/src/online2bin/online2-wav-nnet3-latgen-faster /usr/bin/wav-cpu-decoder
COPY --from=builder /kaldi/src/latbin/lattice-to-ctm-conf /usr/bin/lattice-to-ctm-conf
COPY --from=builder /kaldi/egs/wsj/s5/utils/int2sym.pl /usr/bin/int2sym.pl
COPY --from=builder /kaldi/src/lib/*.so /kaldi/tools/openfst-1.6.7/lib/libfst.so.10 /usr/lib/

WORKDIR /DecodeModel

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
