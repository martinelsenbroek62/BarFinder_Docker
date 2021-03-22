#! /bin/sh

set -e

INPUTDIR=$(dirname $INPUTINDEX)
OUTPUTDIR=$(dirname $OUTPUTINDEX)
mkdir -p $INPUTDIR
mkdir -p $OUTPUTDIR
touch $INPUTINDEX
rm -rf $OUTPUTINDEX; touch $OUTPUTINDEX
cd /langcf

tail -f -n +1 $INPUTINDEX | while read file duration offset; do
    if [ "$file" = "__done__" ]; then
        echo "__done__ -1 -1" >> $3
        exit
    fi
    wavfile=$INPUTDIR/$file
    outfile="$OUTPUTDIR/$(basename $file .wav).log"

    python predict.py \
        --model /langcf/model/2019-07-11-EN-ZH.model  \
        --input $wavfile > $outfile || true

    echo "$(basename $outfile) $duration $offset" >> $3
done
