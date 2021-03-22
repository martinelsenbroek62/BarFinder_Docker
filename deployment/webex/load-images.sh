#! /bin/sh

set -e

cd $(dirname $0)
mkdir -p local
../general/dump-all.sh local
