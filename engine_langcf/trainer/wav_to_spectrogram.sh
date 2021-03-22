#! /bin/bash

set -e

_PWD=$(realpath $(dirname $BASH_SOURCE))

docker run -it --rm \
  --workdir /crnn-lid/data \
  --volume $_PWD/shared:/shared \
  engine_langcf_base:latest \
  python wav_to_spectrogram.py --source /shared/training_data --target /shared/spectrogram_data_huge
