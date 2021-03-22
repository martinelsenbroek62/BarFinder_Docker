#! /bin/bash

set -e

_PWD=$(realpath $(dirname $BASH_SOURCE))

docker run -it --rm --runtime nvidia \
  --workdir /crnn-lid/keras \
  --volume $_PWD/shared:/shared \
  --volume $_PWD/shared/logs:/crnn-lid/keras/logs \
  --volume $_PWD/config.yaml:/crnn-lid/keras/config.yaml \
  engine_langcf_base:latest-gpu \
  python train.py
  
