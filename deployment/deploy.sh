#! /bin/bash

set -e

cd `dirname $0`

. ./env.sh

ssh -t $1 <<EOF
set -e
$(aws ecr get-login --no-include-email --region $AWS_REGION)
mkdir -p DialDocker
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-cpu
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_dial:latest-gpu
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-mandarin
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium-en-us
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_xcel2:latest-tedlium-en-uk
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_diarization:latest
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/api_collection:latest
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/dial_frontend:latest
docker pull 055985172228.dkr.ecr.us-west-2.amazonaws.com/engine_julius:latest-ja
EOF

scp docker-compose.yml $1:DialDocker/
scp create_user.sh $1:DialDocker/
scp start.sh $1:DialDocker/
scp restart.sh $1:DialDocker/
rsync -av --delete certs/certificates/* $1:DialDocker/certs/
ssh -t $1 <<EOF
cd DialDocker
docker-compose up -d --remove-orphans
if ! (crontab -l || true | grep "DialDocker/start\\.sh") ; then
  cat | crontab - <<EOF2
\$(crontab -l)
@reboot DialDocker/start.sh
EOF2
fi
EOF
