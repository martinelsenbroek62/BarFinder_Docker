FROM kaldi_base:latest
# as builder

ENV KALDI_ROOT=/kaldi/

ENV PATH "/kaldi/egs/aspire/s5/utils/:/kaldi/tools/openfst/:/kaldi/src/bin:/kaldi/src/chainbin:/kaldi/src/featbin:/kaldi/src/fgmmbin:/kaldi/src/fstbin:/kaldi/src/gmmbin:/kaldi/src/ivectorbin:/kaldi/src/kwsbin:/kaldi/src/latbin:/kaldi/src/lmbin:/kaldi/src/nnet2bin:/kaldi/src/nnet3bin:/kaldi/src/nnetbin:/kaldi/src/online2bin:/kaldi/src/onlinebin:/kaldi/src/rnnlmbin:/kaldi/src/sgmm2bin:/kaldi/src/sgmmbin:/kaldi/src/tfrnnlmbin/:/kaldi/tools/sctk/bin/:/kaldi/src/cudadecoder/:/kaldi/src/cudadecoderbin/:$PATH"

ENV LC_ALL "C"

ENV train_cmd "run.pl --mem 32G" 
ENV decode_cmd "run.pl --mem 32G"
ENV mkgraph_Cmd "run.pl --mem 32G"

WORKDIR /kaldi/egs/callhome_diarization/v2

COPY 0006_callhome_diarization_v2_1a.tar.gz /kaldi/egs/callhome_diarization/v2/
RUN cd /kaldi/egs/callhome_diarization/v2/ && tar xvzf 0006_callhome_diarization_v2_1a.tar.gz && \
    rm 0006_callhome_diarization_v2_1a.tar.gz && \
    cp -r /kaldi/egs/callhome_diarization/v2/0006_callhome_diarization_v2_1a/exp /kaldi/egs/callhome_diarization/v2/exp && \
    rm -rf /kaldi/egs/callhome_diarization/v2/0006_callhome_diarization_v2_1a

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# FROM nvidia/cuda:9.2-cudnn7-devel-ubuntu16.04
# 
# ENV LC_ALL "C"
# 
# RUN apt-get update -qq && apt-get install -qqy libatlas3-base
# COPY --from=builder /kaldi /kaldi/
# ENV KALDI_ROOT=/kaldi/
# ENV PATH "/kaldi/egs/aspire/s5/utils/:/kaldi/tools/openfst/:/kaldi/src/bin:/kaldi/src/chainbin:/kaldi/src/featbin:/kaldi/src/fgmmbin:/kaldi/src/fstbin:/kaldi/src/gmmbin:/kaldi/src/ivectorbin:/kaldi/src/kwsbin:/kaldi/src/latbin:/kaldi/src/lmbin:/kaldi/src/nnet2bin:/kaldi/src/nnet3bin:/kaldi/src/nnetbin:/kaldi/src/online2bin:/kaldi/src/onlinebin:/kaldi/src/rnnlmbin:/kaldi/src/sgmm2bin:/kaldi/src/sgmmbin:/kaldi/src/tfrnnlmbin/:/kaldi/tools/sctk/bin/:/kaldi/src/cudadecoder/:/kaldi/src/cudadecoderbin/:$PATH"
# 
# WORKDIR /kaldi/egs/callhome_diarization/v2/
