#! /bin/sh

set -e

cd $(dirname $0)/local

ftp -v authenticity.sharefileftp.com <<EOF
prompt
cd PWC\ Installation\ Files/DialDocker2
mput *
EOF
