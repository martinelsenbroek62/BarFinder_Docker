#! /bin/sh

set -e

cd `dirname $0`

. ./env.sh

$(aws ecr get-login --no-include-email --region us-west-2)

docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-cpu
docker tag 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-cpu engine_dial:latest-cpu

docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest
docker tag 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest engine_xcel2:latest

docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-mandarin
docker tag 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-mandarin engine_xcel2:latest-mandarin

docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_diarization:latest
docker tag 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_diarization:latest engine_diarization:latest

docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/api_collection:latest
docker tag 055985172228.dkr.ecr.us-west-2.amazonaws.com/api_collection:latest api_collection:latest

docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/dial_frontend:latest
docker tag 055985172228.dkr.ecr.us-west-2.amazonaws.com/dial_frontend:latest dial_frontend:latest
