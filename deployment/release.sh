#! /bin/sh

set -e

cd `dirname $0`

. ./env.sh

cd ..
make build-dial
make build-kaldi
make build-julius
make build

$(aws ecr get-login --no-include-email --region us-west-2)

docker tag engine_dial:latest-cpu 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-cpu
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-cpu

docker tag engine_dial:latest-gpu 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-gpu
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-gpu

docker tag engine_xcel2:latest 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest

docker tag engine_xcel2:latest-mandarin 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-mandarin
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-mandarin

docker tag engine_xcel2:latest-tedlium 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium

docker tag engine_xcel2:latest-tedlium-en-us 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium-en-us
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium-en-us

docker tag engine_xcel2:latest-tedlium-en-uk 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium-en-uk
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium-en-uk

docker tag engine_julius:latest-ja 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_julius:latest-ja
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_julius:latest-ja

docker tag engine_diarization:latest 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_diarization:latest
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_diarization:latest

docker tag api_collection:latest 055985172228.dkr.ecr.us-west-2.amazonaws.com/api_collection:latest
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/api_collection:latest

docker tag dial_frontend:latest 055985172228.dkr.ecr.us-west-2.amazonaws.com/dial_frontend:latest
docker push 055985172228.dkr.ecr.us-west-2.amazonaws.com/dial_frontend:latest
