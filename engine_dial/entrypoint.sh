#! /bin/sh

set -e

INPUTDIR=$(dirname $INPUTINDEX)
OUTPUTDIR=$(dirname $OUTPUTINDEX)
mkdir -p $INPUTDIR
mkdir -p $OUTPUTDIR
touch $INPUTINDEX
rm -rf $OUTPUTINDEX && touch $OUTPUTINDEX

ARGS="
--trainer_count $TRAINER_COUNT
--alpha ${ALPHA:-0.75}
--beta ${BETA:-1.85}
"

case $DECODE_MODE in
    gpu)
        ARGS="$ARGS --use_gpu"
        ;;
    cpu)
        ARGS="$ARGS"
        ;;
esac

case $AUDIO_LANG in
    zh)
        ARGS="$ARGS
              --rnn_layer_size 1024
              --mean_std_path ./models/cn1k/mean_std.npz
              --vocab_path ./models/cn1k/vocab.txt
              --lang_model_path ./models/lm/zh_giga.no_cna_cmn.prune01244.klm
              --model_path ./models/cn1k/params.tar.gz"
        ;;
    en)
        ARGS="$ARGS
              --rnn_layer_size 1024
              --mean_std_path ./models/en8k/mean_std.npz
              --vocab_path ./models/en8k/vocab.txt
              --lang_model_path ./models/lm/en8k.trie.klm
              --model_path ./models/en8k/params.tar.gz"
        ;;
esac

ARGS="$ARGS --inputindex $INPUTINDEX --outputindex $OUTPUTINDEX"

cd /DecodeEngine
./decode $ARGS
