#! /bin/bash

set -e

INPUTDIR=$(dirname $2)
OUTPUTDIR=$(dirname $3)
mkdir -p $INPUTDIR
mkdir -p $OUTPUTDIR
touch $2
rm -rf $3; touch $3
cd /kaldi/egs/aidatatang_asr

tail -f -n +1 $2 | while read file duration offset; do
    if [ "$file" = "__done__" ]; then
        echo "__done__ -1 -1" >> $3
        exit
    fi
    wavfile=$INPUTDIR/$file
    outfile="$OUTPUTDIR/$(basename $file .wav).log"
    case $1 in
        gpu)
            wav-gpu-decoder \
                --frame-subsampling-factor=${FRAME_SUBSAMPLING_FACTOR} \
                --feature-type=mfcc \
                --mfcc-config=/kaldi/egs/aidatatang_asr/conf/mfcc_hires.conf \
                --max-active=7000 \
                --beam=15.0 \
                --lattice-beam=8.0 \
                --acoustic-scale=1.0 \
                --word-symbol-table=/kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/graph/words.txt \
                /kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/final.mdl \
                /kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/graph/HCLG.fst \
                "scp:echo utterance-id1 $wavfile|" \
                ark:- | lattice-to-ctm-conf --lm-scale=1.5 \
                ark: - | int2sym.pl -f 5 /kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/graph/words.txt > $outfile
            # retVal=$?
            # if [ $retVal -ne 0 -a $retVal -ne 134 ]; then
            #     # we encountered core dumped 134 error but already have the result
            #     false
            # fi
            ;;
        cpu)
            wav-cpu-decoder \
                --online=false \
                --do-endpointing=false \
                --frame-subsampling-factor=${FRAME_SUBSAMPLING_FACTOR} \
                --feature-type=mfcc \
                --fbank-config=/kaldi/egs/aidatatang_asr/conf/mfcc_hires.conf \
                --max-active=7000 \
                --beam=15.0 \
                --lattice-beam=8.0 \
                --acoustic-scale=1.0 \
                --word-symbol-table=/kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/graph/words.txt \
                /kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/final.mdl \
                /kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/graph/HCLG.fst \
                'ark:echo utterance-id1 utterance-id1|' \
                "scp:echo utterance-id1 $wavfile|" \
                ark:- | lattice-to-ctm-conf --lm-scale=1.5 \
                ark: - | int2sym.pl -f 5 /kaldi/egs/aidatatang_asr/exp/chain/tdnn_1a_sp/graph/words.txt > $outfile
            ;;
    esac

    echo "$(basename $outfile) $duration $offset" >> $3
done
