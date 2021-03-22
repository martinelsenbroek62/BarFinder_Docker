#! /bin/bash

set -e

cd `dirname $0`

. ./env.sh

mkdir -p certs
cd certs
docker run \
    -it --rm \
    -e AWS_REGION=${AWS_REGION} \
    -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
    -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
    -v $(pwd):/certs \
    goacme/lego:v3.0.2 \
    --path="/certs" \
    --email="philip.npc@gmail.com" \
    --domains="*.xcellence.tech" \
    --dns="route53" \
    --accept-tos run
sudo chown -R $(id -un):$(id -gn) certs
