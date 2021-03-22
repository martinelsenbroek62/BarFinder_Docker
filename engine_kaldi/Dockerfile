FROM kaldi_base:latest as builder

COPY 0001_aspire_chain_model.tar.gz /kaldi/egs/aspire/s5

RUN cd /kaldi/egs/aspire/s5 && tar xfv 0001_aspire_chain_model.tar.gz && steps/online/nnet3/prepare_online_decoding.sh --mfcc-config conf/mfcc_hires.conf data/lang_chain exp/nnet3/extractor exp/chain/tdnn_7b exp/tdnn_7b_chain_online && utils/mkgraph.sh --self-loop-scale 1.0 data/lang_pp_test exp/tdnn_7b_chain_online exp/tdnn_7b_chain_online/graph_pp && rm -rf /DecodeEngine/0001_aspire_chain_model.tar.gz

RUN rm -rf /kaldi/egs/aspire/s5/exp/tdnn_7b_chain_online/decode_dev
RUN mv /kaldi/egs/aspire/s5/exp/tdnn_7b_chain_online /DecodeModel
RUN sed -i 's!/kaldi/egs/aspire/s5/exp/tdnn_7b_chain_online!/DecodeModel!g' /DecodeModel/conf/ivector_extractor.conf
RUN sed -i 's!/kaldi/egs/aspire/s5/exp/tdnn_7b_chain_online!/DecodeModel!g' /DecodeModel/conf/online.conf


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
# COPY cpu_decoder_wrapper.py /usr/bin/cpu_decoder_wrapper.py
RUN chmod +x /entrypoint.sh
#; chmod +x /usr/bin/cpu_decoder_wrapper.py
