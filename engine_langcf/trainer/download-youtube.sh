#! /bin/bash

set -e

_PWD=$(realpath $(dirname $BASH_SOURCE))

docker run -it --rm --workdir /crnn-lid/data --volume $_PWD/shared:/shared --volume $PWD/sources.yml:/crnn-lid/data/sources.yml engine_langcf_base:latest python download_youtube.py --output /shared --downloads 10000
