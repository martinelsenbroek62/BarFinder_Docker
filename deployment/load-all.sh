#! /bin/sh

set -e

docker load < engine_dial_latest-cpu.tar.gz
docker load < engine_xcel2_latest.tar.gz
docker load < engine_xcel2_latest-mandarin.tar.gz
docker load < engine_julius_latest-ja.tar.gz
docker load < engine_diarization_latest.tar.gz
docker load < api_collection_latest.tar.gz
docker load < dial_frontend_latest.tar.gz
