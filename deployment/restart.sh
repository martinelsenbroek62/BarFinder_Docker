#! /bin/bash
set -e
sudo systemctl start docker.service
cd $(dirname $0)
docker-compose down
docker-compose up -d
