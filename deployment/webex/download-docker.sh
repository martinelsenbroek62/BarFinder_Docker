#! /bin/sh

set -e
cd $(dirname $0)

docker run -i --rm -v $(pwd)/local/docker-install:/docker-install centos:7.6.1810 bash <<EOF
yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2
yum-config-manager \
  --add-repo \
  https://download.docker.com/linux/centos/docker-ce.repo
yum install --downloadonly --downloaddir=/docker-install docker-ce docker-ce-cli containerd.io
curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /docker-install/docker-compose
EOF
