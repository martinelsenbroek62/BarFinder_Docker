#! /bin/bash

set -e

_PWD=$(realpath $(dirname $BASH_SOURCE))

for lang in "english"; do
    docker run -it --rm \
      --workdir /crnn-lid/data/voxforge \
      --volume $_PWD/shared/voxforge/$lang:/crnn-lid/data/voxforge/$lang \
      engine_langcf_base:latest \
      bash download-data.sh $lang
done
