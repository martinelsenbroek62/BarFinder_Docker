#! /bin/bash

set -e

mkdir -p shared/aidatatang

cd shared/aidatatang

curl http://www.openslr.org/resources/62/aidatatang_200zh.tgz -o aidatatang_200zh.tgz
