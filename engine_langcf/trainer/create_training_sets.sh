#! /bin/bash

set -e

_PWD=$(realpath $(dirname $BASH_SOURCE))

docker run -it --rm \
  --workdir /crnn-lid/data \
  --volume $_PWD/shared:/shared \
  engine_langcf_base:latest \
  python create_csv.py --dir /shared/spectrogram_data_huge
