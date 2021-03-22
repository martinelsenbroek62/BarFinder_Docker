build-base:
	@docker build base -t engine_langcf_base:latest --build-arg BASEIMAGE=ubuntu:16.04 --build-arg ENABLE_GPU=false

build-base-gpu:
	@docker build base -t engine_langcf_base:latest-gpu --build-arg BASEIMAGE=nvidia/cuda:8.0-cudnn5-runtime-ubuntu16.04 --build-arg ENABLE_GPU=true

build: build-base
	@docker build . -t engine_langcf:latest

debug:
	@docker run -it --rm --volume $(PWD)/shared:/shared --entrypoint bash engine_langcf:latest

shell-base:
	@docker run -it --rm --volume $(PWD)/shared:/shared engine_langcf_base:latest bash
