FROM kaldi_base:latest

COPY 0010_aidatatang_asr.tar.gz /kaldi/egs

RUN cd /kaldi/egs && tar xvf 0010_aidatatang_asr.tar.gz

# RUN mkdir /DecodeModel
# RUN mv /kaldi/egs/wsj /DecodeModel
# RUN mv /kaldi/egs/aidatatang_asr /DecodeModel
RUN cd /kaldi/egs/aidatatang_asr && \
    ln -s ../wsj/s5/steps/ steps && \
    ln -s ../wsj/s5/utils/ utils
# 
# 
# FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04
# 
# ENV LC_ALL "C"
# 
# RUN apt-get update -qq && apt-get install -qqy libatlas3-base python3 python3-docopt
# 
# COPY --from=builder /DecodeModel /DecodeModel/
RUN cp /kaldi/src/cudadecoderbin/batched-wav-nnet3-cuda /usr/bin/wav-gpu-decoder
RUN cp /kaldi/src/online2bin/online2-wav-nnet3-latgen-faster /usr/bin/wav-cpu-decoder
RUN cp /kaldi/src/latbin/lattice-to-ctm-conf /usr/bin/lattice-to-ctm-conf
RUN cp /kaldi/egs/wsj/s5/utils/int2sym.pl /usr/bin/int2sym.pl
# COPY --from=builder /kaldi/src/lib/*.so /kaldi/tools/openfst-1.6.7/lib/libfst.so.10 /usr/lib/
# 
# WORKDIR /DecodeModel
WORKDIR /kaldi/egs/aidatatang_asr

COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
