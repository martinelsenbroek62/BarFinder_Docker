#! /bin/bash
set -e
sleep 60
sudo systemctl start docker.service
cd $(dirname $0)
docker-compose up -d
