#! /bin/sh

set -e

if [ ! -d $1 ]; then
    echo "Usage: $0 <DEST_DIRECTORY>" 1>&2
    exit 1
fi

cd $1

docker save engine_dial:latest-cpu | pigz > engine_dial_latest-cpu.tar.gz
docker save engine_xcel2:latest | pigz > engine_xcel2_latest.tar.gz
docker save engine_xcel2:latest-mandarin | pigz > engine_xcel2_latest-mandarin.tar.gz
docker save engine_julius:latest-ja | pigz > engine_julius_latest-ja.tar.gz
docker save engine_diarization:latest | pigz > engine_diarization_latest.tar.gz
docker save api_collection:latest | pigz > api_collection_latest.tar.gz
docker save dial_frontend:latest | pigz > dial_frontend_latest.tar.gz
