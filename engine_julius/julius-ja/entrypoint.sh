#! /bin/sh

set -e


INPUTDIR=$(dirname $INPUTINDEX)
OUTPUTDIR=$(dirname $OUTPUTINDEX)
mkdir -p $INPUTDIR
mkdir -p $OUTPUTDIR
touch $INPUTINDEX
rm -rf $OUTPUTINDEX && touch $OUTPUTINDEX
JULIUS_LOG=$OUTPUTDIR/julius.log
JULIUS_OUT=$OUTPUTDIR/julius.out
ADINTOOL_OUT=$OUTPUTDIR/adintool.out

echo $INPUTINDEX
echo $OUTPUTINDEX

tail_follow() {
    tail -f --pid $$ -n +1 $1 | while read file duration offset; do
        if [ "$file" = "__done__" ]; then
            return
        fi
        echo $INPUTDIR/$file
    done
}


DNNCLIENT_SCRIPT=/decode_engine/scripts/dnnclient.py

if [ "$DECODE_MODE" = "gpu" ]; then
    DNNCLIENT_SCRIPT=/decode_engine/scripts/dnnclient-gpu.py
fi

stdbuf -oL julius -C /decode_engine/main.jconf -C /decode_engine/am-dnn.jconf -demo -input vecnet \
    -logfile $JULIUS_LOG -lattice > $JULIUS_OUT &
JULIUS_PID=$!
sleep 10
python $DNNCLIENT_SCRIPT /decode_engine/dnnclient.conf &
sleep 5
tail_follow $INPUTINDEX | stdbuf -oL adintool \
    -in file -out vecnet -server 127.0.0.1 \
    -paramtype FBANK_D_A_Z -veclen 120 \
    -htkconf /decode_engine/model/dnn/config.lmfb \
    -port 5532 -cvn \
    -cmnload /decode_engine/model/dnn/norm -cmnnoupdate > $ADINTOOL_OUT &
python /decode_engine/scripts/parse_output.py $INPUTINDEX $ADINTOOL_OUT $JULIUS_OUT $OUTPUTINDEX
kill $JULIUS_PID || true
